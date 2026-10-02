import logging
from .src.routing.latency_relaxing import LatencyRelaxing
from .src.routing.two_hop_relaxing import TwoHopRelaxing
from .src.routing.composite_metric_relaxing import CompositeMetricRelaxing
from .src.routing.dijkstra_relaxing import DijkstraRelaxing
from .src.routing.stable_relaxing import StableRelaxing
from .src.routing.ecmp_relaxing import ECMPRelaxing

class CloudRouter:
    """
    CloudRouter provides a unified interface for decentralized routing.
    In the AWANTA framework, a Cloud Router instance runs on each edge node.
    """
    STRATEGIES = {
        'latency_relaxing': LatencyRelaxing,
        'two_hop_relaxing': TwoHopRelaxing,
        'composite_metric_relaxing': CompositeMetricRelaxing,
        'dijkstra_relaxing': DijkstraRelaxing,
        'stable_relaxing': StableRelaxing,
        'ecmp_relaxing': ECMPRelaxing,
    }

    def __init__(self, network_manager, datapaths, strategy='latency_relaxing'):
        self.logger = logging.getLogger(__name__)
        strategy_class = self.STRATEGIES.get(strategy)
        if strategy_class:
            self.routing_strategy = strategy_class(network_manager, datapaths)
        else:
            raise ValueError(f"Unknown routing strategy: {strategy}")

    def update_measurements(self, measurement_data):
        """Updates the internal routing matrix with new measurement data."""
        self.routing_strategy.fetch_latency_results(measurement_data)

    def get_route(self, source_dpid, target_dpid):
        """Calculates the optimal route based on current performance metrics."""
        return self.routing_strategy.get_optimal_route(source_dpid, target_dpid)
