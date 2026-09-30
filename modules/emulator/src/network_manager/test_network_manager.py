import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the root directory to sys.path to allow imports from modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from modules.emulator.src.network_manager.network_manager import NetworkManager
from modules.emulator.src.utils.constants import MininetConstants


class TestNetworkManager(unittest.TestCase):
    def setUp(self):
        self.network_manager = NetworkManager()

    def test_initial_links(self):
        # Verify the hardcoded host-switch links set up in __init__
        self.assertEqual(
            self.network_manager.links[MininetConstants.SRC_HOST][MininetConstants.SRC_SWITCH_LABEL],
            (0, 1)
        )
        self.assertEqual(
            self.network_manager.links[MininetConstants.DST_HOST][MininetConstants.DST_SWITCH_LABEL],
            (0, 3)
        )
        self.assertEqual(
            self.network_manager.links[MininetConstants.SRC_SWITCH_LABEL][MininetConstants.SRC_HOST],
            (1, 0)
        )
        self.assertEqual(
            self.network_manager.links[MininetConstants.DST_SWITCH_LABEL][MininetConstants.DST_HOST],
            (3, 0)
        )

    @patch('modules.emulator.src.network_manager.network_manager.get_link')
    @patch('modules.emulator.src.network_manager.network_manager.get_switch')
    def test_initialize_links_adds_switch_links(self, mock_get_switch, mock_get_link):
        # Fake a single link between switch dpid 1 and dpid 2, on ports 5 and 7
        mock_link = MagicMock()
        mock_link.to_dict.return_value = {
            'src': {'dpid': '0000000000000001', 'port_no': '5'},
            'dst': {'dpid': '0000000000000002', 'port_no': '7'}
        }
        mock_get_switch.return_value = []
        mock_get_link.return_value = [mock_link]

        mock_app = MagicMock()
        self.network_manager.initialize_links(mock_app)

        self.assertIn(1, self.network_manager.links)
        self.assertEqual(self.network_manager.links[1][2], (5, 7))

    @patch('modules.emulator.src.network_manager.network_manager.get_link')
    @patch('modules.emulator.src.network_manager.network_manager.get_switch')
    def test_initialize_links_multiple_links(self, mock_get_switch, mock_get_link):
        mock_link_1 = MagicMock()
        mock_link_1.to_dict.return_value = {
            'src': {'dpid': '0000000000000001', 'port_no': '1'},
            'dst': {'dpid': '0000000000000002', 'port_no': '2'}
        }
        mock_link_2 = MagicMock()
        mock_link_2.to_dict.return_value = {
            'src': {'dpid': '0000000000000002', 'port_no': '3'},
            'dst': {'dpid': '0000000000000003', 'port_no': '4'}
        }
        mock_get_switch.return_value = []
        mock_get_link.return_value = [mock_link_1, mock_link_2]

        mock_app = MagicMock()
        self.network_manager.initialize_links(mock_app)

        self.assertEqual(self.network_manager.links[1][2], (1, 2))
        self.assertEqual(self.network_manager.links[2][3], (3, 4))


if __name__ == '__main__':
    unittest.main()