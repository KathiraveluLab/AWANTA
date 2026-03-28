from .routing import Routing

class LatencyRelaxing(Routing):
    """
    Extracted from emulator. This is a latency relaxing algorithm.
    """

    def __init__(self, network_manager, datapaths):
        super().__init__(network_manager, datapaths)

    def get_optimal_route(self, source_dpid, target_dpid):
        source_index = self.link_to_index[source_dpid]
        target_index = self.link_to_index[target_dpid]
        direct_link = self.rtt_matrix[source_index][target_index]
        one_hop_node = None
        output_dpids = [source_dpid]

        for j in range(len(self.rtt_matrix)):
            if j == source_index or j == target_index:
                continue
            latency = self.rtt_matrix[source_index][j] + self.rtt_matrix[j][target_index]
            if latency < direct_link:
                direct_link = latency
                one_hop_node = self.index_to_link[j]

        if one_hop_node != None:
            output_dpids.append(one_hop_node)
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
