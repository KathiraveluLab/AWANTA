import stomp
import json
import logging

class EventManager:
    """
    EventManager handles the propagation of measurement changes as events
    to an ActiveMQ broker using the STOMP protocol.
    """
    def __init__(self, host='localhost', port=61613, destination='/queue/awanta.events'):
        self.host = host
        self.port = port
        self.destination = destination
        self.conn = None
        self.logger = logging.getLogger(__name__)

    def _connect(self):
        """Internal method to establish connection to the broker."""
        try:
            self.conn = stomp.Connection([(self.host, self.port)])
            self.conn.connect(wait=True)
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to ActiveMQ broker at {self.host}:{self.port} - {e}")
            return False

    def publish_measurement(self, data):
        """
        Publishes measurement data to the configured destination.
        
        :param data: Dictionary containing measurement results.
        """
        if not self.conn or not self.conn.is_connected():
            if not self._connect():
                return False
        
        try:
            message = json.dumps(data)
            self.conn.send(body=message, destination=self.destination)
            self.logger.info(f"Published event to {self.destination}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to publish event: {e}")
            return False

    def disconnect(self):
        """Disconnects from the broker."""
        if self.conn and self.conn.is_connected():
            self.conn.disconnect()
            self.logger.info("Disconnected from ActiveMQ broker")

if __name__ == "__main__":
    # Small test block if run directly
    logging.basicConfig(level=logging.INFO)
    em = EventManager()
    test_data = {"test": "latency", "value": 25.5}
    success = em.publish_measurement(test_data)
    if success:
        print("Test publish successful!")
    else:
        print("Test publish failed (Broker might be offline).")
    em.disconnect()
