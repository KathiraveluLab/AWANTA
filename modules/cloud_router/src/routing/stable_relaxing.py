import sys
from .routing import Routing
from .latency_relaxing import LatencyRelaxing


class StableRelaxing(Routing):
    """
    Wraps another routing strategy and adds route stability. A newly
    computed route is only adopted if it improves on the currently
    committed route's total latency by more than `switch_margin` (a
    fraction, e.g. 0.1 = 10%). Otherwise the previously chosen route is
    kept, even if the freshly recomputed "optimal" route differs slightly.

    Motivation: every measurement cycle, a bare strategy recomputes the
    best route from scratch. If two paths have nearly identical latency,
    ordinary measurement noise can cause the "best" route to flip back and
    forth every cycle. For telehealth video/audio traffic, that flapping
    (and the reconnect/jitter it causes) is often worse than staying on a
    slightly-suboptimal-but-stable path. If the current route becomes
    completely unreachable, this always switches immediately regardless of
    margin, since stability should never mean staying on a dead path.
    """

    def __init__(self, network_manager, datapaths, inner_strategy_class=None, switch_margin: float = 0.1):
        super().__init__(network_manager, datapaths)
        if inner_strategy_class is None:
            inner_strategy_class = LatencyRelaxing
        self.inner_strategy = inner_strategy_class(network_manager, datapaths)
        self.switch_margin = switch_margin
        self.current_route = None
        self.current_route_cost = None

    def update_rtt_matrix(self, latency_results):
        self.inner_strategy.update_rtt_matrix(latency_results)
        self.rtt_matrix = self.inner_strategy.rtt_matrix

    def _route_cost(self, route):
        total = 0
        for i in range(len(route) - 1):
            a = self.link_to_index[route[i]]
            b = self.link_to_index[route[i + 1]]
            total += self.rtt_matrix[a][b]
        return total

    def get_optimal_route(self, source_dpid, target_dpid):
        candidate_route = self.inner_strategy.get_optimal_route(source_dpid, target_dpid)
        candidate_cost = self._route_cost(candidate_route)

        if self.current_route is None:
            self.current_route = candidate_route
            self.current_route_cost = candidate_cost
            return self.current_route

        self.current_route_cost = self._route_cost(self.current_route)

        if self.current_route_cost >= sys.maxsize:
            self.current_route = candidate_route
            self.current_route_cost = candidate_cost
            return self.current_route

        if self.current_route_cost == 0:
            return self.current_route

        improvement = (self.current_route_cost - candidate_cost) / self.current_route_cost
        if improvement > self.switch_margin:
            self.logger.info(
                "Switching route from %s (cost %.2f) to %s (cost %.2f): %.1f%% improvement exceeds margin",
                self.current_route, self.current_route_cost, candidate_route, candidate_cost, improvement * 100
            )
            self.current_route = candidate_route
            self.current_route_cost = candidate_cost

        return self.current_route