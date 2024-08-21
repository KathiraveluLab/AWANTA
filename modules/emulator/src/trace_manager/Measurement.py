class Measurement:
    """Stores the metric of a single measurement

    :param src: The unique node id
    :type src: int
    :param metric: This is the measurement metric, this could be latency, or bandwidth, or throughput etc.
    :type metric: any
    """
    def __init__(self, src: int, metric: any):
        self.src = src
        self.metric = metric