import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add modules to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'modules', 'event_manager')))

from EventManager import EventManager

class TestEventManager(unittest.TestCase):
    @patch('stomp.Connection')
    def test_publish_measurement(self, mock_connection_class):
        # Setup mock connection
        mock_conn = MagicMock()
        mock_connection_class.return_value = mock_conn
        mock_conn.is_connected.side_effect = [False, True] # First check false, then true after connect
        
        em = EventManager(host='localhost', port=61613)
        test_data = {"test": "latency", "value": 25.5}
        
        success = em.publish_measurement(test_data)
        
        # Verify connect was called
        mock_conn.connect.assert_called_once()
        # Verify send was called with correct data
        mock_conn.send.assert_called_once()
        args, kwargs = mock_conn.send.call_args
        self.assertEqual(kwargs['destination'], '/queue/awanta.events')
        self.assertIn('"test": "latency"', kwargs['body'])
        self.assertTrue(success)

    @patch('stomp.Connection')
    def test_disconnect(self, mock_connection_class):
        mock_conn = MagicMock()
        mock_connection_class.return_value = mock_conn
        mock_conn.is_connected.return_value = True
        
        em = EventManager()
        em._connect()
        em.disconnect()
        
        mock_conn.disconnect.assert_called_once()

if __name__ == '__main__':
    unittest.main()
