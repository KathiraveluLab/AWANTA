import unittest
import sys
import os
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.cloud_router.src.routing.composite_metric_relaxing import CompositeMetricRelaxing
from modules.emulator.src.trace_manager.Measurement import Measurement


class TestCompositeMetricRelaxing(unittest.TestCase):
    def setUp(self):
        self.router = CompositeMetricRelaxing(MagicMock(), {})
        self.router.link_to_index = {1: 0, 2: 1, 3: 2}
        self.router.index_to_link = {0: 1, 1: 2, 2: 3}
        self.router.rtt_matrix = [[sys.maxsize for _ in range(3)] for _ in range(3)]
        self.router.jitter_matrix = [[0.0 for _ in range(3)] for _ in range(3)]
        self.router.hop_count_matrix = [[0 for _ in range(3)] for _ in range(3)]

    def test_update_rtt_matrix_records_rtt_jitter_and_hop_count(self):
        latency_results = [
            Measurement(1, {"2": 10, "3": 50}, jitter=1.5, hop_count=2),
        ]
        self.router.update_rtt_matrix(latency_results)

        self.assertEqual(self.router.rtt_matrix[0][1], 10)
        self.assertEqual(self.router.jitter_matrix[0][1], 1.5)
        self.assertEqual(self.router.hop_count_matrix[0][1], 2)

    def test_behaves_like_pure_rtt_when_jitter_and_hops_are_zero(self):
        # With no jitter/hop penalty, this should match LatencyRelaxing's baseline behavior.
        self.router.rtt_matrix[0][1] = 10
        self.router.rtt_matrix[1][2] = 15
        self.router.rtt_matrix[0][2] = 50

        route = self.router.get_optimal_route(1, 3)
        self.assertEqual(route, [1, 2, 3])

    def test_high_jitter_on_lower_latency_direct_link_favors_relaxed_path(self):
        # Direct link has the lowest raw RTT, but very high jitter makes it
        # unattractive relative to a slightly slower but stable relayed path.
        self.router.rtt_matrix[0][2] = 20         # s1-s3 direct: fast...
        self.router.jitter_matrix[0][2] = 50       # ...but extremely jittery
        self.router.rtt_matrix[0][1] = 15          # s1-s2
        self.router.rtt_matrix[1][2] = 15          # s2-s3 (total RTT: 30, worse than direct's 20)
        # jitter/hop on the relayed path left at 0 (clean, stable path)

        route = self.router.get_optimal_route(1, 3)
        self.assertEqual(route, [1, 2, 3])

    def test_hop_count_penalty_can_tip_a_close_decision(self):
        self.router.rtt_matrix[0][2] = 30           # s1-s3 direct
        self.router.rtt_matrix[0][1] = 14           # s1-s2
        self.router.rtt_matrix[1][2] = 15           # s2-s3 (total RTT: 29, barely better than direct)
        self.router.hop_count_matrix[0][1] = 10      # but this hop is reported as high hop-count/unstable

        # hop_weight default 5.0 * 10 hops = 50 penalty, easily outweighing the 1ms RTT saving
        route = self.router.get_optimal_route(1, 3)
        self.assertEqual(route, [1, 3])

    def test_custom_weights_are_respected(self):
        router = CompositeMetricRelaxing(MagicMock(), {}, jitter_weight=0.0, hop_weight=0.0)
        router.link_to_index = {1: 0, 2: 1, 3: 2}
        router.index_to_link = {0: 1, 1: 2, 2: 3}
        router.rtt_matrix = [[sys.maxsize for _ in range(3)] for _ in range(3)]
        router.jitter_matrix = [[0.0 for _ in range(3)] for _ in range(3)]
        router.hop_count_matrix = [[0 for _ in range(3)] for _ in range(3)]

        # With weights zeroed out, jitter/hop_count should have no effect at all.
        router.rtt_matrix[0][2] = 20
        router.jitter_matrix[0][2] = 999
        router.hop_count_matrix[0][2] = 999
        router.rtt_matrix[0][1] = 15
        router.rtt_matrix[1][2] = 15

        route = router.get_optimal_route(1, 3)
        self.assertEqual(route, [1, 3])  # direct still wins on pure RTT since penalties are disabled


if __name__ == '__main__':
    unittest.main()