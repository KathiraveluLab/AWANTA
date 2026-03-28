class Measurement:
    """Stores the metric of a single measurement

    :param src: The unique node id
    :type src: int
    :param metric: This is the measurement metric, this could be latency, or bandwidth, or throughput etc.
    :type metric: any
    :param jitter: The standard deviation of the latency measurements.
    :type jitter: float
    :param hop_count: The number of network hops in the path.
    :type hop_count: int
    """
    def __init__(self, src: int, metric: any, jitter: float = 0.0, hop_count: int = 0):
        self.src = src
        self.metric = metric
        self.jitter = jitter
        self.hop_count = hop_count