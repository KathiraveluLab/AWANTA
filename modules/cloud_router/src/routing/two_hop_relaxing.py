from .routing import Routing

class TwoHopRelaxing(Routing):
    """
    Extends the single-hop relaxation idea used by LatencyRelaxing to also
    consider two-hop detours. LatencyRelaxing only checks whether a single
    intermediate node beats the direct link; on topologies larger than a
    full mesh of 3 nodes, a route via two intermediate nodes can sometimes
    beat both the direct link and any single available one-hop detour.
    This strategy checks direct, one-hop, and two-hop candidate paths and
    picks whichever has the lowest total latency.
    """

    def __init__(self, network_manager, datapaths):
        super().__init__(network_manager, datapaths)

    def get_optimal_route(self, source_dpid, target_dpid):
        source_index = self.link_to_index[source_dpid]
        target_index = self.link_to_index[target_dpid]
        n = len(self.rtt_matrix)

        best_latency = self.rtt_matrix[source_index][target_index]
        best_path_indices = []  # intermediate hop indices, in order

        # Check every single-hop detour: source -> j -> target
        for j in range(n):
            if j == source_index or j == target_index:
                continue
            latency = self.rtt_matrix[source_index][j] + self.rtt_matrix[j][target_index]
            if latency < best_latency:
                best_latency = latency
                best_path_indices = [j]

        # Check every two-hop detour: source -> j -> k -> target
        for j in range(n):
            if j == source_index or j == target_index:
                continue
            for k in range(n):
                if k == source_index or k == target_index or k == j:
                    continue
                latency = (
                    self.rtt_matrix[source_index][j]
                    + self.rtt_matrix[j][k]
                    + self.rtt_matrix[k][target_index]
                )
                if latency < best_latency:
                    best_latency = latency
                    best_path_indices = [j, k]

        output_dpids = [source_dpid]
        output_dpids.extend(self.index_to_link[i] for i in best_path_indices)
        output_dpids.append(target_dpid)
        return output_dpids

    def update_rtt_matrix(self, latency_results):
        for measurement in latency_results:
            source_dpid = measurement.src
            latency_data = measurement.metric
            source_index = self.link_to_index[source_dpid]
            for dpid, latency in latency_data.items():
                target_index = self.link_to_index[int(dpid)]
                self.rtt_matrix[source_index][target_index] = latency