from modules.cloud_router.src.routing.composite_metric_relaxing import CompositeMetricRelaxing

routing = {
    "latency_relaxing": LatencyRelaxing,
    "two_hop_relaxing": TwoHopRelaxing,
    "composite_metric_relaxing": CompositeMetricRelaxing,
}