import unittest
import sys
import os
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.cloud_router.src.routing.ecmp_relaxing import ECMPRelaxing


class TestECMPRelaxing(unittest.TestCase):
    def _make_router(self, n):
        router = ECMPRelaxing(MagicMock(), {})
        router.link_to_index = {i + 1: i for i in range(n)}
        router.index_to_link = {i: i + 1 for i in range(n)}
        router.rtt_matrix = [[sys.maxsize for _ in range(n)] for _ in range(n)]
        return router

    def test_single_path_when_no_alternate_exists(self):
        router = self._make_router(3)
        router.rtt_matrix[0][1] = 10
        router.rtt_matrix[1][2] = 10
        # No other links at all, so only one route from 1 to 3 is possible.

        results = router.get_k_shortest_paths(1, 3, k=2)
        self.assertEqual(len(results), 1)
        path, weight = results[0]
        self.assertEqual(path, [1, 2, 3])
        self.assertAlmostEqual(weight, 1.0)

    def test_two_equal_cost_disjoint_paths_split_evenly(self):
        # 4 nodes: two totally separate paths of equal cost from 1 to 4.
        router = self._make_router(4)
        router.rtt_matrix[0][1] = 10   # 1 -> 2
        router.rtt_matrix[1][3] = 10   # 2 -> 4  (path A total: 20)
        router.rtt_matrix[0][2] = 10   # 1 -> 3
        router.rtt_matrix[2][3] = 10   # 3 -> 4  (path B total: 20)

        results = router.get_k_shortest_paths(1, 4, k=2)
        self.assertEqual(len(results), 2)
        weights = sorted(w for _, w in results)
        self.assertAlmostEqual(weights[0], 0.5, places=3)
        self.assertAlmostEqual(weights[1], 0.5, places=3)

    def test_much_worse_alternate_excluded_by_tolerance(self):
        router = self._make_router(4)
        router.rtt_matrix[0][1] = 10
        router.rtt_matrix[1][3] = 10   # best path total: 20
        router.rtt_matrix[0][2] = 100
        router.rtt_matrix[2][3] = 100  # alternate total: 200, far outside tolerance

        results = router.get_k_shortest_paths(1, 4, k=2, tolerance=0.15)
        self.assertEqual(len(results), 1)

    def test_weights_favor_the_cheaper_of_two_within_tolerance_paths(self):
        router = self._make_router(4)
        router.rtt_matrix[0][1] = 10
        router.rtt_matrix[1][3] = 10   # best path total: 20
        router.rtt_matrix[0][2] = 11
        router.rtt_matrix[2][3] = 11   # alternate total: 22 (within 15% tolerance of 20)

        results = router.get_k_shortest_paths(1, 4, k=2, tolerance=0.15)
        self.assertEqual(len(results), 2)
        best = next(w for p, w in results if p == [1, 2, 4])
        alt = next(w for p, w in results if p == [1, 3, 4])
        self.assertGreater(best, alt)

    def test_weights_always_sum_to_one(self):
        router = self._make_router(4)
        router.rtt_matrix[0][1] = 10
        router.rtt_matrix[1][3] = 10
        router.rtt_matrix[0][2] = 11
        router.rtt_matrix[2][3] = 11

        results = router.get_k_shortest_paths(1, 4, k=2, tolerance=0.15)
        total_weight = sum(w for _, w in results)
        self.assertAlmostEqual(total_weight, 1.0, places=6)

    def test_get_optimal_route_returns_single_best_path_for_compatibility(self):
        router = self._make_router(4)
        router.rtt_matrix[0][1] = 10
        router.rtt_matrix[1][3] = 10
        router.rtt_matrix[0][2] = 11
        router.rtt_matrix[2][3] = 11

        route = router.get_optimal_route(1, 4)
        self.assertEqual(route, [1, 2, 4])
        self.assertIsInstance(route, list)


if __name__ == '__main__':
    unittest.main()