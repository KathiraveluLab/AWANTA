from modules.cloud_router.src.routing.latency_relaxing import LatencyRelaxing
from modules.cloud_router.src.routing.dijkstra_relaxing import DijkstraRelaxing
<<<<<<< HEAD
from modules.cloud_router.src.routing.ecmp_relaxing import ECMPRelaxing
=======
from modules.cloud_router.src.routing.stable_relaxing import StableRelaxing
>>>>>>> upstream/main

routing = {
    "latency_relaxing": LatencyRelaxing,
    "dijkstra_relaxing": DijkstraRelaxing,
<<<<<<< HEAD
    "ecmp_relaxing": ECMPRelaxing,
=======
    "stable_relaxing": StableRelaxing,
>>>>>>> upstream/main
}