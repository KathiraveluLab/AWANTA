import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.cloud_router.src.routing.two_hop_relaxing import TwoHopRelaxing
from modules.emulator.src.trace_manager.Measurement import Measurement


class TestTwoHopRelaxing(unittest.TestCase):
    def setUp(self):
        from unittest.mock import MagicMock
        self.mock_network_manager = MagicMock()
        self.mock_datapaths = {}
        self.router = TwoHopRelaxing(self.mock_network_manager, self.mock_datapaths)

        # 4 nodes: s1, s2, s3, s4 -> indices 0, 1, 2, 3
        self.router.link_to_index = {1: 0, 2: 1, 3: 2, 4: 3}
        self.router.index_to_link = {0: 1, 1: 2, 2: 3, 3: 4}
        self.router.rtt_matrix = [[sys.maxsize for _ in range(4)] for _ in range(4)]

    def test_update_rtt_matrix(self):
        latency_results = [
            Measurement(1, {"2": 10, "3": 50}),
            Measurement(2, {"1": 10, "3": 15}),
        ]
        self.router.update_rtt_matrix(latency_results)

        self.assertEqual(self.router.rtt_matrix[0][1], 10)
        self.assertEqual(self.router.rtt_matrix[0][2], 50)
        self.assertEqual(self.router.rtt_matrix[1][0], 10)
        self.assertEqual(self.router.rtt_matrix[1][2], 15)

    def test_direct_path_wins_when_it_is_shortest(self):
        # s1-s4 direct is far cheaper than any detour
        self.router.rtt_matrix[0][3] = 5
        self.router.rtt_matrix[0][1] = 100
        self.router.rtt_matrix[1][3] = 100

        route = self.router.get_optimal_route(1, 4)
        self.assertEqual(route, [1, 4])

    def test_one_hop_wins_over_direct(self):
        # s1-s4 direct is expensive; s1-s2-s4 is cheaper
        self.router.rtt_matrix[0][3] = 100
        self.router.rtt_matrix[0][1] = 10
        self.router.rtt_matrix[1][3] = 15

        route = self.router.get_optimal_route(1, 4)
        self.assertEqual(route, [1, 2, 4])

    def test_two_hop_wins_over_direct_and_one_hop(self):
        # Direct is expensive, the only one-hop option is mediocre,
        # but a two-hop path via s2 -> s3 is the cheapest overall.
        self.router.rtt_matrix[0][3] = 100   # direct s1-s4
        self.router.rtt_matrix[0][1] = 40    # s1-s2
        self.router.rtt_matrix[1][3] = 45    # s2-s4 (one-hop total: 85)
        self.router.rtt_matrix[0][1] = 10    # s1-s2 (reused for two-hop path)
        self.router.rtt_matrix[1][2] = 10    # s2-s3
        self.router.rtt_matrix[2][3] = 10    # s3-s4 (two-hop total: 30)

        route = self.router.get_optimal_route(1, 4)
        self.assertEqual(route, [1, 2, 3, 4])

    def test_no_beneficial_detour_falls_back_to_direct(self):
        self.router.rtt_matrix[0][3] = 10
        # All other links are expensive, so nothing beats the direct link
        for i in range(4):
            for j in range(4):
                if i != j and not (i == 0 and j == 3):
                    self.router.rtt_matrix[i][j] = 1000

        route = self.router.get_optimal_route(1, 4)
        self.assertEqual(route, [1, 4])


if __name__ == '__main__':
    unittest.main()