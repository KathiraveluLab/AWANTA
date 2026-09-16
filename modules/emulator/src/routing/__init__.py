from modules.cloud_router.src.routing.latency_relaxing import LatencyRelaxing
from modules.cloud_router.src.routing.dijkstra_relaxing import DijkstraRelaxing
from modules.cloud_router.src.routing.stable_relaxing import StableRelaxing

routing = {
    "latency_relaxing": LatencyRelaxing,
    "dijkstra_relaxing": DijkstraRelaxing,
    "stable_relaxing": StableRelaxing,
}