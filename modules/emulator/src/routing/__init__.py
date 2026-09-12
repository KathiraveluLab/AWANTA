from modules.cloud_router.src.routing.latency_relaxing import LatencyRelaxing
from modules.cloud_router.src.routing.dijkstra_relaxing import DijkstraRelaxing
from modules.cloud_router.src.routing.ecmp_relaxing import ECMPRelaxing

routing = {
    "latency_relaxing": LatencyRelaxing,
    "dijkstra_relaxing": DijkstraRelaxing,
    "ecmp_relaxing": ECMPRelaxing,
}