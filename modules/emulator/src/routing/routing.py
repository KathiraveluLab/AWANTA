import logging
import sys
from abc import ABC, abstractmethod

from ..trace_manager.Measurement import Measurement
from ..utils.constants import ControllerConstants, MininetConstants
from ..utils.utils import preprocess_ids


class Routing(ABC):

    def __init__(self, network_manager, datapaths):
        self.datapaths = datapaths
        self.network_manager = network_manager
        self.rtt_matrix = [[sys.maxsize for _ in range(MininetConstants.NUM_FULL_MESH)] for _ in
                           range(MininetConstants.NUM_FULL_MESH)]
        self.link_to_index = {k: k - 1 for k in range(1, MininetConstants.NUM_FULL_MESH + 1)}
        self.index_to_link = {v: s for s, v in self.link_to_index.items()}
        self.logger = logging.getLogger(ControllerConstants.LOGGER_NAME)

    @abstractmethod
    def update_rtt_matrix(self, latency_results: list[Measurement]):
        pass

    def fetch_latency_results(self, latency_results: list[Measurement]):

        self.update_rtt_matrix(latency_results)
        dp_ids: list[str] = self.get_optimal_route(MininetConstants.SRC_SWITCH_LABEL, MininetConstants.DST_SWITCH_LABEL)
        self.set_optimal_route(dp_ids)

    @abstractmethod
    def get_optimal_route(self, source_dpid, target_dpid) -> list[str]:
        pass

    def set_ip_flow(self, x, y, z):
        datapath = self.datapaths[y]
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inport = self.network_manager.links[x][y][1]
        match = parser.OFPMatch(in_port=inport)
        outport = self.network_manager.links[y][z][0]
        actions = [parser.OFPActionOutput(outport)]
        self.add_flow(datapath, ControllerConstants.FLOW_PRIORITY, match, actions)

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

        dpids.append(MininetConstants.DST_HOST)
        dpids = [MininetConstants.SRC_HOST] + dpids
        self.logger.info("Routing Path: %s", preprocess_ids(dpids.copy()))

        for i in range(len(dpids)):
            if i + 1 > len(dpids) - 1:
                continue
            elif i - 1 < 0:
                continue

            self.set_ip_flow(dpids[i - 1], dpids[i], dpids[i + 1])
            self.set_ip_flow(dpids[i + 1], dpids[i], dpids[i - 1])
