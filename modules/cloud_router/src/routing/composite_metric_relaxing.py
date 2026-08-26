import sys
from .routing import Routing


class CompositeMetricRelaxing(Routing):
    """
    Extends the single-hop relaxation idea used by LatencyRelaxing, but
    scores candidate paths using a composite of RTT, jitter, and hop count
    instead of RTT alone.

    Motivation: AWANTA's measurement pipeline (see EventTraceManager and
    MeasurementsClient) already captures jitter and hop count alongside RTT,
    but every existing routing strategy discards them and optimizes on raw
    RTT only. For AWANTA's actual use case, telehealth traffic, jitter
    matters disproportionately for real-time audio/video quality, and hop
    count is a reasonable proxy for path stability (more hops generally
    means more points of failure and reconfiguration risk). This strategy
    factors both in explicitly, rather than ignoring signal the pipeline
    already collects.

    Scoring: score = rtt + (jitter_weight * jitter) + (hop_weight * hop_count)

    RTT remains the dominant term (weight 1), so this strategy reduces to
    the same behavior as LatencyRelaxing when jitter and hop_count are zero
    or unavailable. The default weights (jitter_weight=2.0, hop_weight=5.0)
    reflect jitter being penalized more per unit than latency, and hop count
    acting as a smaller tie-breaking/stability adjustment; both are
    configurable since the right weighting is deployment-specific.
    """

    def __init__(self, network_manager, datapaths, jitter_weight: float = 2.0, hop_weight: float = 5.0):
        super().__init__(network_manager, datapaths)
        self.jitter_weight = jitter_weight
        self.hop_weight = hop_weight
        n = len(self.rtt_matrix)
        self.jitter_matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        self.hop_count_matrix = [[0 for _ in range(n)] for _ in range(n)]

    def _composite_score(self, i: int, j: int) -> float:
        rtt = self.rtt_matrix[i][j]
        if rtt == sys.maxsize:
            # Unmeasured/unreachable link: never let jitter or hop count
            # make this look attractive relative to a measured link.
            return sys.maxsize
        return rtt + (self.jitter_weight * self.jitter_matrix[i][j]) + (self.hop_weight * self.hop_count_matrix[i][j])

    def get_optimal_route(self, source_dpid, target_dpid):
        source_index = self.link_to_index[source_dpid]
        target_index = self.link_to_index[target_dpid]
        direct_score = self._composite_score(source_index, target_index)
        one_hop_node = None
        output_dpids = [source_dpid]

        for j in range(len(self.rtt_matrix)):
            if j == source_index or j == target_index:
                continue
            candidate_score = self._composite_score(source_index, j) + self._composite_score(j, target_index)
            if candidate_score < direct_score:
                direct_score = candidate_score
                one_hop_node = self.index_to_link[j]

        if one_hop_node is not None:
            output_dpids.append(one_hop_node)
        output_dpids.append(target_dpid)
        return output_dpids

    def update_rtt_matrix(self, latency_results):
        for measurement in latency_results:
            source_dpid = measurement.src
            source_index = self.link_to_index[source_dpid]
            latency_data = measurement.metric

            for dpid, latency in latency_data.items():
                target_index = self.link_to_index[int(dpid)]
                self.rtt_matrix[source_index][target_index] = latency

            # jitter and hop_count are per-measurement (one value per source
            # node for this update cycle), not per-target like latency_data,
            # so they're recorded against every target this source reported on.
            for dpid in latency_data.keys():
                target_index = self.link_to_index[int(dpid)]
                self.jitter_matrix[source_index][target_index] = measurement.jitter
                self.hop_count_matrix[source_index][target_index] = measurement.hop_count