import sys

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib import hub
import json
import os


class Controller(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Controller, self).__init__(*args, **kwargs)
        # monitor = Monitor()
        self.datapath_ids = {}
        self.rtt_matrix = [[-sys.maxsize for _ in range(3)] for _ in range(3)]
        self.network_graph = [[[0 for _ in range(3)] for _ in range(3)]]
        self.measurement_count = 0
        self.link_to_index = {"s1":0, "s12": 1, "s2": 2}
        self.ip_mapping = {"s1": "10.0.0.1", "s12": "10.0.0.2", "s2": "10.0.0.3"}
        self.index_to_link = {v:s for s, v in self.link_to_index.items()}
        self.latency_data = self.process_files()
        self.latency_monitor = hub.spawn(self.fetch_latency_results())


    def process_files(self):
        print("here")
        with open("modules/emulator/measurements/s1.json") as s1_m:
            s1_data = json.load(s1_m)

        with open("modules/emulator/measurements/s2.json") as s2_m:
            s2_data = json.load(s2_m)

        with open("modules/emulator/measurements/s12.json") as s12_m:
            s12_data = json.load(s12_m)

        return {"s1": s1_data, "s12": s12_data, "s2": s2_data}

    @set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapath_ids:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapath_ids[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapath_ids:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapath_ids[datapath.id]



    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Add table miss flow entries
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]

        self.logger.info('OFPSwitchFeatures received: '
                          'datapath_id=0x%016x n_buffers=%d '
                          'n_tables=%d auxiliary_id=%d '
                          'capabilities=0x%08x',
                          ev.msg.datapath_id, ev.msg.n_buffers, ev.msg.n_tables,
                          ev.msg.auxiliary_id, ev.msg.capabilities)
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)

        datapath.send_msg(mod)


    def set_ip_flow(self, datapath, source_dpid, destination_dpid):
        datapath = datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        srcip = self.ip_mapping[source_dpid]
        dstip = self.ip_mapping[destination_dpid]

        match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP,
                                ipv4_src=srcip,
                                ipv4_dst=dstip
                                )
        # self.add_flow(datapath, 1, match, actions)


    def fetch_latency_results(self):

        print(os.getcwd())

        for dpid, latency_data in self.latency_data.items():
            ld = latency_data[self.measurement_count]
            self._update_rtt_matrix(dpid, ld)

        self.measurement_count += 1




        # self._update_rtt_matrix(s1_data, s2_data, s12_data)
        # self._set_optimal_route()

        hub.sleep(30)


    def _update_rtt_matrix(self, source_dpid, latency_data):

        source_index = self.link_to_index[source_dpid]

        for dpid, latency in latency_data.items():
            target_index = self.link_to_index[dpid]
            self.rtt_matrix[source_index][target_index] = latency

    def _set_optimal_route(self, source_dpid, target_dpid):

        source_index = self.link_to_index[source_dpid]
        target_index = self.link_to_index[target_dpid]

        direct_link = self.rtt_matrix[source_index][target_index]
        one_hop_node = None

        for i in range(source_index, len(self.rtt_matrix)):

            for j in range(target_index):

                if self.rtt_matrix[i][j] + self.rtt_matrix[j][target_index] < direct_link:
                    direct_link = self.rtt_matrix[i][j] + self.rtt_matrix[j][target_index]
                    # Update path specific link
                    one_hop_node = self.index_to_link[j]


        if one_hop_node != None:
            self.set_ip_flow(self.datapath_ids[source_dpid[1:]], source_dpid, target_dpid)







