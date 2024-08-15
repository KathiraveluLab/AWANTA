import logging
import sys

from modules.emulator.src.routing.routing import Routing
from modules.emulator.src.utils.constants import MininetConstants, ControllerConstants
from utils import preprocess_ids


class LatencyRelaxing(Routing):

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


