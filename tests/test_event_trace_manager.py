import sys
import os
import unittest
from unittest.mock import MagicMock, patch
import queue

# Add modules to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'modules', 'event-manager')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'modules', 'emulator')))

from EventManager import EventManager
from src.trace_manager.event_trace_manager import EventTraceManager
from src.trace_manager.Measurement import Measurement

class TestEventTraceManager(unittest.TestCase):
    @patch('EventManager.stomp.Connection')
    def test_event_flow(self, mock_connection_class):
        # Setup mock connection
        mock_conn = MagicMock()
        mock_connection_class.return_value = mock_conn
        mock_conn.is_connected.return_value = True
        
        # Initialize ET Manager
        etm = EventTraceManager()
        etm.process_files() # This should call subscribe
        
        # Verify subscribe was called on EventManager
        # We need to get the callback passed to subscribe
        args, kwargs = mock_conn.set_listener.call_args
        listener = kwargs.get('listener') or args[1]
        
        # Simulate an incoming message with jitter and hop count
        test_data_json = '{"country": "AD", "data": {"99.79.30.74": {"rtt": 25.5, "jitter": 1.2, "hop_count": 5}}}'
        frame = MagicMock()
        frame.body = test_data_json
        listener.on_message(frame)
        
        # Get next state from ET Manager
        state = etm.get_next_state()
        
        self.assertIsNotNone(state)
        self.assertEqual(len(state), 1)
        self.assertIsInstance(state[0], Measurement)
        self.assertEqual(state[0].metric, 25.5)
        self.assertEqual(state[0].jitter, 1.2)
        self.assertEqual(state[0].hop_count, 5)

if __name__ == '__main__':
    unittest.main()
