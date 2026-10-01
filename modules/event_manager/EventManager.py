import stomp
import json
import logging

class EventListener(stomp.ConnectionListener):
    def __init__(self, callback):
        self.callback = callback
        self.logger = logging.getLogger(__name__)

    def on_error(self, frame):
        self.logger.error(f'Received an error: {frame.body}')

    def on_message(self, frame):
        try:
            data = json.loads(frame.body)
            self.callback(data)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON message: {e}")
        except Exception as e:
            self.logger.error(f"Failed to process message: {e}")


class EventManager:
    """
    EventManager handles the propagation of measurement changes as events
    to an ActiveMQ broker using the STOMP protocol.
    """
    def __init__(self, host='localhost', port=61613, destination='/queue/awanta.events'):
        self._validate_connection_params(host, port, destination)
        self.host = host
        self.port = port
        self.destination = destination
        self.conn = None
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def _validate_connection_params(host, port, destination):
        """
        Validates connection parameters up front, so a misconfigured host,
        port, or destination fails immediately with a clear message instead
        of surfacing later as an opaque error from deep inside the stomp
        library.
        """
        errors = []

        if not isinstance(host, str) or not host.strip():
            errors.append("'host' must be a non-empty string")

        if not isinstance(port, int) or isinstance(port, bool) or not (1 <= port <= 65535):
            errors.append("'port' must be an integer between 1 and 65535")

        if not isinstance(destination, str) or not destination.strip():
            errors.append("'destination' must be a non-empty string")

        if errors:
            error_message = "Invalid EventManager connection parameters:\n  - " + "\n  - ".join(errors)
            raise ValueError(error_message)

    def _connect(self):
        """Internal method to establish connection to the broker."""
        try:
            self.conn = stomp.Connection([(self.host, self.port)])
            self.conn.connect(wait=True)
            return True
        except stomp.exception.ConnectFailedException as e:
            self.logger.error(f"Failed to connect to ActiveMQ broker (Connection Failed) at {self.host}:{self.port} - {e}")
            return False
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

    def subscribe(self, callback):
        """
        Subscribes to measurement events and triggers the callback.
        
        :param callback: Function to call when an event is received.
        """
        if not self.conn or not self.conn.is_connected():
            if not self._connect():
                return False
        
        try:
            self.conn.set_listener('awanta_listener', EventListener(callback))
            self.conn.subscribe(destination=self.destination, id=1, ack='auto')
            self.logger.info(f"Subscribed to {self.destination}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to subscribe: {e}")
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
    
    def my_callback(data):
        print(f"Callback received: {data}")

    if em.subscribe(my_callback):
        test_data = {"test": "latency", "value": 25.5}
        em.publish_measurement(test_data)
        # Give it a second to receive
        import time
        time.sleep(1)
    
    em.disconnect()