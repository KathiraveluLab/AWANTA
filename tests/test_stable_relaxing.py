import unittest
import sys
import os
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.cloud_router.src.routing.stable_relaxing import StableRelaxing


class TestStableRelaxing(unittest.TestCase):
    def _make_router(self, n=3, margin=0.1):
        mock_inner_class = MagicMock()
        mock_inner_instance = MagicMock()
        mock_inner_class.return_value = mock_inner_instance

        router = StableRelaxing(MagicMock(), {}, inner_strategy_class=mock_inner_class, switch_margin=margin)
        router.link_to_index = {i + 1: i for i in range(n)}
        router.index_to_link = {i: i + 1 for i in range(n)}
        router.rtt_matrix = [[sys.maxsize for _ in range(n)] for _ in range(n)]
        router.inner_strategy = mock_inner_instance
        return router

    def test_first_call_adopts_whatever_inner_strategy_returns(self):
        router = self._make_router()
        router.rtt_matrix[0][1] = 10
        router.inner_strategy.get_optimal_route.return_value = [1, 2]

        route = router.get_optimal_route(1, 2)
        self.assertEqual(route, [1, 2])

    def test_marginal_improvement_below_threshold_keeps_current_route(self):
        router = self._make_router(n=3, margin=0.10)
        router.rtt_matrix[0][1] = 100
        router.inner_strategy.get_optimal_route.return_value = [1, 2]
        router.get_optimal_route(1, 2)

        router.rtt_matrix[0][2] = 47
        router.rtt_matrix[2][1] = 48
        router.inner_strategy.get_optimal_route.return_value = [1, 3, 2]

        route = router.get_optimal_route(1, 2)
        self.assertEqual(route, [1, 2])

    def test_significant_improvement_above_threshold_switches(self):
        router = self._make_router(n=3, margin=0.10)
        router.rtt_matrix[0][1] = 100
        router.inner_strategy.get_optimal_route.return_value = [1, 2]
        router.get_optimal_route(1, 2)

        router.rtt_matrix[0][2] = 15
        router.rtt_matrix[2][1] = 15
        router.inner_strategy.get_optimal_route.return_value = [1, 3, 2]

        route = router.get_optimal_route(1, 2)
        self.assertEqual(route, [1, 3, 2])

    def test_unreachable_current_route_forces_switch_regardless_of_margin(self):
        router = self._make_router(n=3, margin=0.5)
        router.rtt_matrix[0][1] = 10
        router.inner_strategy.get_optimal_route.return_value = [1, 2]
        router.get_optimal_route(1, 2)

        router.rtt_matrix[0][1] = sys.maxsize
        router.rtt_matrix[0][2] = 500
        router.rtt_matrix[2][1] = 500
        router.inner_strategy.get_optimal_route.return_value = [1, 3, 2]

        route = router.get_optimal_route(1, 2)
        self.assertEqual(route, [1, 3, 2])

    def test_custom_margin_is_respected(self):
        router = self._make_router(n=3, margin=0.01)
        router.rtt_matrix[0][1] = 100
        router.inner_strategy.get_optimal_route.return_value = [1, 2]
        router.get_optimal_route(1, 2)

        router.rtt_matrix[0][2] = 48
        router.rtt_matrix[2][1] = 49
        router.inner_strategy.get_optimal_route.return_value = [1, 3, 2]

        route = router.get_optimal_route(1, 2)
        self.assertEqual(route, [1, 3, 2])


if __name__ == '__main__':
    unittest.main()