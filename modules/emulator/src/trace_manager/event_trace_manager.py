from __future__ import annotations
import queue
import logging
import os
import sys

from .Measurement import Measurement
from .NodeMeasurement import NodeMeasurement
from .TraceManager import TraceManager

# Add event-manager to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'event-manager')))
from EventManager import EventManager

class EventTraceManager(TraceManager):
    """
    EventTraceManager receives real-time measurement events from ActiveMQ
    and provides them to the controller via the TraceManager interface.
    """
    def __init__(self, path=None):
        # path is not used but kept for interface compatibility
        super().__init__(path)
        self.event_queue = queue.Queue()
        self.event_manager = EventManager()
        self.logger = logging.getLogger(__name__)

    def _event_callback(self, data):
        """Callback triggered when a new measurement event arrives."""
        try:
            self.logger.info(f"Received measurement event for {data.get('country')}")
            # Map country/data to Measurement objects
            # For prototype, we assume 'country' string can be converted/mapped to dpid
            # or we just use a placeholder if mapping is complex
            country = data.get('country', '0')
            measurements_dict = data.get('data', {})
            
            measurements: list[Measurement] = []
            for target, metrics in measurements_dict.items():
                try:
                    src_id = int(hash(country) % 100) # Placeholder mapping
                    if isinstance(metrics, dict):
                        rtt = metrics.get('rtt', 0.0)
                        jitter = metrics.get('jitter', 0.0)
                        hop_count = metrics.get('hop_count', 0)
                        measurements.append(Measurement(src_id, float(rtt or 0.0), float(jitter or 0.0), int(hop_count or 0)))
                    else:
                        # Legacy support for simple RTT values
                        measurements.append(Measurement(src_id, float(metrics)))
                except Exception as e:
                    self.logger.warning(f"Failed to process measurement for target {target}: {e}")
                    continue
            
            if measurements:
                self.event_queue.put(measurements)
        except Exception as e:
            self.logger.error(f"Error in event callback: {e}")

    def process_files(self):
        """Initializes the subscription."""
        self.logger.info("Initializing EventTraceManager subscription...")
        if not self.event_manager.subscribe(self._event_callback):
            self.logger.error("Failed to subscribe to measurement events!")

    def get_next_state(self) -> list[Measurement] | None:
        """Returns the next set of measurements from the queue (blocking with timeout)."""
        try:
            # Wait for an event for a short time to allow the monitor loop to be responsive
            return self.event_queue.get(timeout=1.0)
        except queue.Empty:
            return [] # Return empty list if no new data, monitor loop will sleep and retry

    def close(self):
        """Explicitly disconnect from the event manager."""
        if hasattr(self, 'event_manager'):
            self.event_manager.disconnect()

    def __del__(self):
        self.close()
