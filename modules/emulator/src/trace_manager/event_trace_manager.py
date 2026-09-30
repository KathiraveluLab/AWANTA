from __future__ import annotations
import queue
import json
import logging
import os
import sys

from .Measurement import Measurement
from .NodeMeasurement import NodeMeasurement
from .TraceManager import TraceManager

from modules.event_manager.EventManager import EventManager
from modules.emulator.src.utils.constants import MininetConstants

DEFAULT_MAPPING_FILE = os.path.join(os.path.dirname(__file__), "country_dpid_mapping.json")


class EventTraceManager(TraceManager):
    """
    EventTraceManager receives real-time measurement events from ActiveMQ
    and provides them to the controller via the TraceManager interface.
    """
    def __init__(self, path=None, country_mapping_path=None):
        # path is not used but kept for interface compatibility
        super().__init__(path)
        self.event_queue = queue.Queue()
        self.event_manager = EventManager()
        self.logger = logging.getLogger(__name__)
        self.country_dpid_map = self._load_country_mapping(country_mapping_path)
        self._unmapped_countries_warned = set()

    def _load_country_mapping(self, country_mapping_path):
        """
        Loads a country -> dpid mapping from a JSON file. Falls back to an
        empty mapping (with a logged warning) if no file is found, in which
        case _map_country_to_dpid() will use its hash-based fallback for
        every country instead.
        """
        mapping_path = country_mapping_path or DEFAULT_MAPPING_FILE
        try:
            with open(mapping_path, 'r') as f:
                raw_mapping = json.load(f)
            # Normalize country codes to upper-case and dpids to int
            return {str(country).upper(): int(dpid) for country, dpid in raw_mapping.items()}
        except (FileNotFoundError, json.JSONDecodeError, AttributeError, ValueError, TypeError) as e:
            self.logger.warning(
                f"Could not load country-dpid mapping from {mapping_path} ({e}). "
                f"Falling back to hash-based mapping for all countries."
            )
            return {}

    def _map_country_to_dpid(self, country):
        """
        Maps a country code to a switch dpid. Uses the configured mapping
        file when the country is present there; otherwise falls back to a
        deterministic hash spread across the actual number of switches in
        the topology (NUM_FULL_MESH), instead of an arbitrary range that
        may not correspond to any real switch.
        """
        normalized_country = str(country).upper()
        if normalized_country in self.country_dpid_map:
            return self.country_dpid_map[normalized_country]

        if normalized_country not in self._unmapped_countries_warned:
            self.logger.warning(
                f"No explicit dpid mapping for country '{country}'. "
                f"Using hash-based fallback across {MininetConstants.NUM_FULL_MESH} switches."
            )
            self._unmapped_countries_warned.add(normalized_country)

        # Spread unmapped countries across the switches that actually exist,
        # with dpids starting at 1 (matching the topology's numbering).
        import zlib
        return (zlib.adler32(normalized_country.encode('utf-8')) % MininetConstants.NUM_FULL_MESH) + 1

    def _event_callback(self, data):
        """Callback triggered when a new measurement event arrives."""
        try:
            self.logger.info(f"Received measurement event for {data.get('country')}")
            country = data.get('country', '0')
            measurements_dict = data.get('data', {})

            src_id = self._map_country_to_dpid(country)

            measurements: list[Measurement] = []
            for target, metrics in measurements_dict.items():
                try:
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