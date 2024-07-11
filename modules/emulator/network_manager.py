import copy

from ryu.topology.api import get_switch, get_link
from constants import NetworkManagerConstants
from utils import convert_dpid_key
from constants import MininetConstants
import logging

class NetworkManager:

    def __init__(self):
        self.links = dict()
        self.links[MininetConstants.SRC_HOST] = {}
        self.links[MininetConstants.DST_HOST] = {}
        self.links[MininetConstants.SRC_SWITCH_LABEL] = {}
        self.links[MininetConstants.DST_SWITCH_LABEL] = {}
        self.links[MininetConstants.SRC_HOST][MininetConstants.SRC_SWITCH_LABEL] = (0, 1)
        self.links[MininetConstants.DST_HOST][MininetConstants.DST_SWITCH_LABEL] = (0, 3)
        self.links[MininetConstants.SRC_SWITCH_LABEL][MininetConstants.SRC_HOST] = (1, 0)
        self.links[MininetConstants.DST_SWITCH_LABEL][MininetConstants.DST_HOST] = (3, 0)

    def initialize_links(self, app):
        self.topo_raw_switches = copy.copy(get_switch(app, None))
        self.topo_raw_links = copy.copy(get_link(app, None))

        for l in self.topo_raw_links:
            link = l.to_dict()
            src = link[NetworkManagerConstants.SRC]
            dst = link[NetworkManagerConstants.DST]
            self.links[convert_dpid_key(src[NetworkManagerConstants.DP_ID])] = self.links.get(convert_dpid_key(src[NetworkManagerConstants.DP_ID]), {})
            self.links[convert_dpid_key(src[NetworkManagerConstants.DP_ID])][convert_dpid_key(dst[NetworkManagerConstants.DP_ID])] = (int(src[NetworkManagerConstants.PORT_NO]), int(dst[NetworkManagerConstants.PORT_NO]))