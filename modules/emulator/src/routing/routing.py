import logging
import sys
from abc import ABC, abstractmethod

from ..trace_manager.Measurement import Measurement
from ..utils.constants import ControllerConstants, MininetConstants
from ..utils.utils import preprocess_ids


class Routing(ABC):
    """This is a base class for routing strategies. Each newly implemented routing strategy should inherit from this class. Each new routing strategy should implement :func: `update_rtt_matrix` and :func: `get_optimal_route`

    :param network_manager: The network manager object :class: `NetworkManager`
    :type network_manager: class:`NetworkManager`
    :param datapaths: The datapaths map that stores datapath id of the corresponding virtual mininet switch
    :type datapaths: dict[str: ]
    """

    def __init__(self, network_manager, datapaths):
        """Constructor method
        """
        self.datapaths = datapaths
        self.network_manager = network_manager
        self.rtt_matrix = [[sys.maxsize for _ in range(MininetConstants.NUM_FULL_MESH)] for _ in
                           range(MininetConstants.NUM_FULL_MESH)]
        self.link_to_index = {k: k - 1 for k in range(1, MininetConstants.NUM_FULL_MESH + 1)}
        self.index_to_link = {v: s for s, v in self.link_to_index.items()}
        self.logger = logging.getLogger(ControllerConstants.LOGGER_NAME)

    @abstractmethod
    def update_rtt_matrix(self, latency_results: list[Measurement]) -> None:
        """Takes a list of :class: `Measurement` objects and updates the RTT matrix

        :param latency_results: A list of measurement objects that need to be injected into the virtual mininet topology aka rtt matrix
        :type latency_results: list[Measurement]
        :return: Does not return anything
        :rtype: None
        """
        pass

    def fetch_latency_results(self, latency_results: list[Measurement]) -> None:
        """Takes a list of :class: `Measurement` objects and performs the following functions
            1. update rtt matrix
            2. calculate the optimal route from source label to destination label
            3. set the optimal route in the underlying mininet topology using SDN controller

        :param latency_results: A list of measurement objects that need to be injected into the virtual mininet topology aka rtt matrix
        :type latency_results: list[Measurement]
        :return: Does not return anything
        :rtype: None
        """

        self.update_rtt_matrix(latency_results)
        dp_ids: list[str] = self.get_optimal_route(MininetConstants.SRC_SWITCH_LABEL, MininetConstants.DST_SWITCH_LABEL)
        self.set_optimal_route(dp_ids)

    @abstractmethod
    def get_optimal_route(self, source_dpid: int, target_dpid: int) -> list[str]:
        """This is an abstract method, that can be overridden by subclasses. Each subclass implements this method and performs its own strategy to calculate the optimal route. This function is utilized to calculate the optimal route between the source and destination nodes, and return the list of nodes that are contained in this optimal route.

        :param source_dpid: Datapath id of the source node
        :type source_dpid: int
        :param target_dpid: Datapath id of the target node
        :type target_dpid: int
        :return: A list of datapath switch names
        :rtype: list[str]
        """
        pass

    def set_ip_flow(self, x: str, y: str, z: str) -> None:
        """Takes in a series of 3 nodes, (x, y, z) and forms links in between them, i.e forms x-y link, y-z link, and y-x link, z-y link

        :param x: node name
        :type x: str
        :param y: node name
        :type y: str
        :param z: node name
        :type z: str
        :return: Does not return anything
        :rtype: None
        """
        datapath = self.datapaths[y]
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inport = self.network_manager.links[x][y][1]
        match = parser.OFPMatch(in_port=inport)
        outport = self.network_manager.links[y][z][0]
        actions = [parser.OFPActionOutput(outport)]
        self.add_flow(datapath, ControllerConstants.FLOW_PRIORITY, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None) -> None:
        """Performs flow addition in the mininet topology using SDN controller.

        :param datapath: Ryu switch datapath object
        :type datapath: ryu.controller.controller.Datapath
        :param priority: Flow priority
        :type priority: int
        :param match: Ryu OFPMatch object
        :type match: ryu.ofproto.ofproto_v1_2_parser.OFPMatch
        :param actions: Ryu SDN actions
        :type actions: ryu.ofproto.ofproto_v1_2_parser.OFPActionOutput
        :param buffer_id: Packet Buffer Id - ID assigned by datapath (OFP_NO_BUFFER if none)
        :type buffer_id: int | None
        :return: Does not return anything
        :rtype: None
        """
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

    def set_optimal_route(self, dpids: list[str]) -> None:
        """Takes in a list of node names, which form a path from source to destination, and sets up the optimal route in the mininet topology using the SDN controller.

        :param dpids: A list of node names
        :type dpids: list[str]
        :return: Does not return anything
        :rtype: None
        """

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
