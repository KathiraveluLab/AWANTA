import unittest
import sys
import os
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.cloud_router.src.routing.dijkstra_relaxing import DijkstraRelaxing


class TestDijkstraRelaxing(unittest.TestCase):
    def _make_router(self, n):
        router = DijkstraRelaxing(MagicMock(), {})
        router.link_to_index = {i + 1: i for i in range(n)}
        router.index_to_link = {i: i + 1 for i in range(n)}
        router.rtt_matrix = [[sys.maxsize for _ in range(n)] for _ in range(n)]
        return router

    def test_direct_path_wins_when_shortest(self):
        router = self._make_router(3)
        router.rtt_matrix[0][2] = 5
        router.rtt_matrix[0][1] = 100
        router.rtt_matrix[1][2] = 100

        self.assertEqual(router.get_optimal_route(1, 3), [1, 3])

    def test_finds_path_longer_than_two_hops(self):
        # 5 nodes: the true shortest path needs 3 intermediate hops,
        # which TwoHopRelaxing's fixed depth limit could never find.
        router = self._make_router(5)
        router.rtt_matrix[0][4] = 1000       # direct s1-s5: expensive
        router.rtt_matrix[0][1] = 10          # s1-s2
        router.rtt_matrix[1][2] = 10          # s2-s3
        router.rtt_matrix[2][3] = 10          # s3-s4
        router.rtt_matrix[3][4] = 10          # s4-s5 (total: 40, via 3 intermediate hops)

        self.assertEqual(router.get_optimal_route(1, 5), [1, 2, 3, 4, 5])

    def test_unreachable_target_falls_back_to_direct_link(self):
        router = self._make_router(3)
        # No links at all are populated (everything stays at sys.maxsize)

        self.assertEqual(router.get_optimal_route(1, 3), [1, 3])

    def test_update_rtt_matrix(self):
        from modules.emulator.src.trace_manager.Measurement import Measurement
        router = self._make_router(2)
        router.update_rtt_matrix([Measurement(1, {"2": 15})])
        self.assertEqual(router.rtt_matrix[0][1], 15)


if __name__ == '__main__':
    unittest.main()