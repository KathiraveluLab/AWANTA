import sys


class Routing:

    def __init__(self, network_manager, latency_data, datapaths):
        self.datapaths = datapaths
        self.network_manager = network_manager
        self.latency_data = latency_data
        self.rtt_matrix = [[sys.maxsize for _ in range(3)] for _ in range(3)]
        self.measurement_count = 0
        self.link_to_index = {1: 0, 12: 1, 2: 2}
        self.index_to_link = {v:s for s, v in self.link_to_index.items()}

    def fetch_latency_results(self):

        print("Fetching latency results")
        for dpid, latency_data in self.latency_data.items():
            ld = latency_data[self.measurement_count]
            self._update_rtt_matrix(dpid, ld)
        self.measurement_count += 1

        print(self.rtt_matrix)
        dpids = self.get_optimal_route(1, 2)
        self.set_optimal_route(dpids)

    def _update_rtt_matrix(self, source_dpid, latency_data):

        source_index = self.link_to_index[source_dpid]

        for dpid, latency in latency_data.items():
            target_index = self.link_to_index[int(dpid)]
            self.rtt_matrix[source_index][target_index] = latency


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

    def set_ip_flow(self, x, y, z):
        datapath = self.datapaths[y]
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inport = self.network_manager.links[x][y][1]
        match = parser.OFPMatch(in_port=inport)
        outport = self.network_manager.links[y][z][0]
        actions = [parser.OFPActionOutput(outport)]
        self.add_flow(datapath, 2, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        instruction = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod_message = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=instruction)
        else:
            mod_message = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=instruction)

        datapath.send_msg(mod_message)

    def set_optimal_route(self, dpids):

        dpids.append('h2')
        dpids = ['h1'] + dpids

        print(dpids)

        for i in range(len(dpids)):
            if i + 1 > len(dpids) - 1:
                continue
            elif i - 1 < 0:
                continue

            self.set_ip_flow(dpids[i-1], dpids[i], dpids[i+1])
            self.set_ip_flow(dpids[i+1], dpids[i], dpids[i-1])