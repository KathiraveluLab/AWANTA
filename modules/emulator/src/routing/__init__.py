from modules.cloud_router.src.routing.latency_relaxing import LatencyRelaxing
from modules.cloud_router.src.routing.two_hop_relaxing import TwoHopRelaxing

routing = {
    "latency_relaxing": LatencyRelaxing,
    "two_hop_relaxing": TwoHopRelaxing,
}