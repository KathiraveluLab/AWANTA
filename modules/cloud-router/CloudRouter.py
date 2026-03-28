import logging
from .src.routing.latency_relaxing import LatencyRelaxing

class CloudRouter:
    """
    CloudRouter provides a unified interface for decentralized routing.
    In the AWANTA framework, a Cloud Router instance runs on each edge node.
    """
    def __init__(self, network_manager, datapaths, strategy='latency_relaxing'):
        self.logger = logging.getLogger(__name__)
        if strategy == 'latency_relaxing':
            self.routing_strategy = LatencyRelaxing(network_manager, datapaths)
        else:
            raise ValueError(f"Unknown routing strategy: {strategy}")

    def update_measurements(self, measurement_data):
        """Updates the internal routing matrix with new measurement data."""
        self.routing_strategy.fetch_latency_results(measurement_data)

    def get_route(self, source_dpid, target_dpid):
        """Calculates the optimal route based on current performance metrics."""
        return self.routing_strategy.get_optimal_route(source_dpid, target_dpid)
