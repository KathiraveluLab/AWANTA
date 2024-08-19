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
    def update_rtt_matrix(self, latency_results: list[Measurement]):
        """Returns a list of :class:`bluepy.blte.Service` objects representing
        the services offered by the device. This will perform Bluetooth service
        discovery if this has not already been done; otherwise it will return a
        cached list of services immediately..

        :param uuids: A list of string service UUIDs to be discovered,
            defaults to None
        :type uuids: list, optional
        :return: A list of the discovered :class:`bluepy.blte.Service` objects,
            which match the provided ``uuids``
        :rtype: list On Python 3.x, this returns a dictionary view object,
            not a list
        """
        pass

    def fetch_latency_results(self, latency_results: list[Measurement]):
        """Returns a list of :class:`bluepy.blte.Service` objects representing
        the services offered by the device. This will perform Bluetooth service
        discovery if this has not already been done; otherwise it will return a
        cached list of services immediately..

        :param uuids: A list of string service UUIDs to be discovered,
            defaults to None
        :type uuids: list, optional
        :return: A list of the discovered :class:`bluepy.blte.Service` objects,
            which match the provided ``uuids``
        :rtype: list On Python 3.x, this returns a dictionary view object,
            not a list
        """

        self.update_rtt_matrix(latency_results)
        dp_ids: list[str] = self.get_optimal_route(MininetConstants.SRC_SWITCH_LABEL, MininetConstants.DST_SWITCH_LABEL)
        self.set_optimal_route(dp_ids)

    @abstractmethod
    def get_optimal_route(self, source_dpid, target_dpid) -> list[str]:
        """Returns a list of :class:`bluepy.blte.Service` objects representing
        the services offered by the device. This will perform Bluetooth service
        discovery if this has not already been done; otherwise it will return a
        cached list of services immediately..

        :param uuids: A list of string service UUIDs to be discovered,
            defaults to None
        :type uuids: list, optional
        :return: A list of the discovered :class:`bluepy.blte.Service` objects,
            which match the provided ``uuids``
        :rtype: list On Python 3.x, this returns a dictionary view object,
            not a list
        """
        pass

    def set_ip_flow(self, x, y, z):
        """Returns a list of :class:`bluepy.blte.Service` objects representing
        the services offered by the device. This will perform Bluetooth service
        discovery if this has not already been done; otherwise it will return a
        cached list of services immediately..

        :param uuids: A list of string service UUIDs to be discovered,
            defaults to None
        :type uuids: list, optional
        :return: A list of the discovered :class:`bluepy.blte.Service` objects,
            which match the provided ``uuids``
        :rtype: list On Python 3.x, this returns a dictionary view object,
            not a list
        """
        datapath = self.datapaths[y]
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inport = self.network_manager.links[x][y][1]
        match = parser.OFPMatch(in_port=inport)
        outport = self.network_manager.links[y][z][0]
        actions = [parser.OFPActionOutput(outport)]
        self.add_flow(datapath, ControllerConstants.FLOW_PRIORITY, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        """Returns a list of :class:`bluepy.blte.Service` objects representing
        the services offered by the device. This will perform Bluetooth service
        discovery if this has not already been done; otherwise it will return a
        cached list of services immediately..

        :param uuids: A list of string service UUIDs to be discovered,
            defaults to None
        :type uuids: list, optional
        :return: A list of the discovered :class:`bluepy.blte.Service` objects,
            which match the provided ``uuids``
        :rtype: list On Python 3.x, this returns a dictionary view object,
            not a list
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

    def set_optimal_route(self, dpids):
        """Returns a list of :class:`bluepy.blte.Service` objects representing
        the services offered by the device. This will perform Bluetooth service
        discovery if this has not already been done; otherwise it will return a
        cached list of services immediately..

        :param uuids: A list of string service UUIDs to be discovered,
            defaults to None
        :type uuids: list, optional
        :return: A list of the discovered :class:`bluepy.blte.Service` objects,
            which match the provided ``uuids``
        :rtype: list On Python 3.x, this returns a dictionary view object,
            not a list
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
