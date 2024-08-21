from .routing import Routing


class LatencyRelaxing(Routing):
    """This is a latency relaxing algorithm, that chooses the best next one-hop node as the routing strategy. For example, let's say we have three nodes s1, s2, s3.
    Let s1 be the source node and s3 be the destination node. If latency of s1-s2 + latency of s2-s3 < latency of s1-s3, then the optimal route from s1-s3 is changed as s1-s2-s3.

    :param network_manager: The network manager object :class: `NetworkManager`
    :type network_manager: class:`NetworkManager`
    :param datapaths: The datapaths map that stores datapath id of the corresponding virtual mininet switch
    :type datapaths: dict[str: ryu.controller.controller.Datapath]
    """

    def __init__(self, network_manager, datapaths):
        super().__init__(network_manager, datapaths)

    def get_optimal_route(self, source_dpid, target_dpid):
        source_index = self.link_to_index[source_dpid]
        target_index = self.link_to_index[target_dpid]

        direct_link = self.rtt_matrix[source_index][target_index]
        one_hop_node = None

        output_dpids = []
        output_dpids.append(source_dpid)

        for i in range(source_index, len(self.rtt_matrix)):

            for j in range(target_index):

                if self.rtt_matrix[i][j] + self.rtt_matrix[j][target_index] < direct_link:
                    direct_link = self.rtt_matrix[i][j] + self.rtt_matrix[j][target_index]
                    # Update path specific link
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


