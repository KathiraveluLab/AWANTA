import copy
import json
import sys

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
from ryu.topology import event
from ryu.topology.api import get_link, get_switch

from network_manager import NetworkManager
from routing import Routing
from trace_manager import TraceManager


class Controller(app_manager.RyuApp):

    def __init__(self, *args, **kwargs):
        super(Controller, self).__init__(*args, **kwargs)
        self.network_manager = NetworkManager()
        self.trace_manager = TraceManager("")
        self.latency_data = self.trace_manager.process_files()
        self.datapaths = {}
        self.routing = Routing(self.network_manager, self.latency_data, self.datapaths)
        self.monitor_thread = hub.spawn(self._monitor)

    @set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]


    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        # self.topo_raw_switches = copy.copy(get_switch(self, datapath.id))
        # print(self.topo_raw_switches[0].to_dict())

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


    def _monitor(self):
        while True:
            if len(self.datapaths) != 0:
                self.routing.fetch_latency_results()
            hub.sleep(10)

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




    def set_ip_flow(self, x, y, z):
        datapath = self.datapaths[y]
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inport = self.links[x][y][1]
        match = parser.OFPMatch(in_port=inport)
        outport = self.links[y][z][0]
        actions = [parser.OFPActionOutput(outport)]
        self.add_flow(datapath, 2, match, actions)


    def _fetch_latency_results(self):

        print("Fetching latency results")
        for dpid, latency_data in self.latency_data.items():
            ld = latency_data[self.measurement_count]
            self._update_rtt_matrix(dpid, ld)
        self.measurement_count += 1


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

    @set_ev_cls(event.EventSwitchEnter)
    def handler_switch_enter(self, ev):
        # The Function get_switch(self, None) outputs the list of switches.
        # self.topo_raw_switches = copy.copy(get_switch(self, None))
        # # The Function get_link(self, None) outputs the list of links.
        # self.topo_raw_links = copy.copy(get_link(self, None))
        #
        # for l in self.topo_raw_links:
        #     link = l.to_dict()
        #     src = link['src']
        #     dst = link['dst']
        #     self.links[int(src['dpid'], 16)] = self.links.get(int(src['dpid'], 16), {})
        #     self.links[int(src['dpid'], 16)][int(dst['dpid'], 16)] = (int(src['port_no']), int(dst['port_no']))
        self.network_manager.initialize_links(self)
