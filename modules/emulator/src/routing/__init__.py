from modules.cloud_router.src.routing.latency_relaxing import LatencyRelaxing
from modules.cloud_router.src.routing.two_hop_relaxing import TwoHopRelaxing
from modules.cloud_router.src.routing.composite_metric_relaxing import CompositeMetricRelaxing
from modules.cloud_router.src.routing.dijkstra_relaxing import DijkstraRelaxing
from modules.cloud_router.src.routing.stable_relaxing import StableRelaxing
from modules.cloud_router.src.routing.ecmp_relaxing import ECMPRelaxing

routing = {
    "latency_relaxing": LatencyRelaxing,
    "two_hop_relaxing": TwoHopRelaxing,
    "composite_metric_relaxing": CompositeMetricRelaxing,
    "dijkstra_relaxing": DijkstraRelaxing,
    "stable_relaxing": StableRelaxing,
    "ecmp_relaxing": ECMPRelaxing,
}
