import unittest
from unittest.mock import MagicMock
import sys
import os

# Add the root directory to sys.path to allow imports from modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from modules.emulator.src.routing.latency_relaxing import LatencyRelaxing
from modules.emulator.src.trace_manager.Measurement import Measurement
from modules.emulator.src.utils.constants import MininetConstants

class TestLatencyRelaxing(unittest.TestCase):
    def setUp(self):
        self.mock_network_manager = MagicMock()
        self.mock_datapaths = {}
        self.latency_relaxing = LatencyRelaxing(self.mock_network_manager, self.mock_datapaths)

        # Explicitly set the mappings to ensure the test is deterministic and independent of MininetConstants
        # s1: index 0, s2: index 1, s3: index 2
        self.latency_relaxing.link_to_index = {1: 0, 2: 1, 3: 2}
        self.latency_relaxing.index_to_link = {0: 1, 1: 2, 2: 3}

        # Reset RTT matrix to a known state
        self.latency_relaxing.rtt_matrix = [[sys.maxsize for _ in range(3)] for _ in range(3)]

    def test_update_rtt_matrix(self):
        # Create dummy latency results
        # Measurement(src, metric) where metric is a dict {dpid: latency}
        latency_results = [
            Measurement(1, {"2": 10, "3": 50}),
            Measurement(2, {"1": 10, "3": 15})
        ]

        self.latency_relaxing.update_rtt_matrix(latency_results)

        self.assertEqual(self.latency_relaxing.rtt_matrix[0][1], 10)
        self.assertEqual(self.latency_relaxing.rtt_matrix[0][2], 50)
        self.assertEqual(self.latency_relaxing.rtt_matrix[1][0], 10)
        self.assertEqual(self.latency_relaxing.rtt_matrix[1][2], 15)

        # Verify other entries remain sys.maxsize
        self.assertEqual(self.latency_relaxing.rtt_matrix[2][0], sys.maxsize)

    def test_get_optimal_route_direct(self):
        # Set up RTT matrix for a direct path being optimal
        # s1-s2: 10, s2-s3: 15, s1-s3: 20
        # 10 + 15 = 25 > 20, so s1-s3 direct is better
        self.latency_relaxing.rtt_matrix[0][1] = 10
        self.latency_relaxing.rtt_matrix[1][2] = 15
        self.latency_relaxing.rtt_matrix[0][2] = 20

        route = self.latency_relaxing.get_optimal_route(1, 3)
        self.assertEqual(route, [1, 3])

    def test_get_optimal_route_relaxed(self):
        # Set up RTT matrix for a relaxed path being optimal
        # s1-s2: 10, s2-s3: 15, s1-s3: 50
        # 10 + 15 = 25 < 50, so s1-s2-s3 is better
        self.latency_relaxing.rtt_matrix[0][1] = 10
        self.latency_relaxing.rtt_matrix[1][2] = 15
        self.latency_relaxing.rtt_matrix[0][2] = 50

        route = self.latency_relaxing.get_optimal_route(1, 3)
        self.assertEqual(route, [1, 2, 3])

if __name__ == '__main__':
    unittest.main()
