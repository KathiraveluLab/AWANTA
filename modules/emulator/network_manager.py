import copy

from ryu.topology.api import get_switch, get_link


class NetworkManager:

    def __init__(self):
        self.links = dict()
        self.links['h1'] = {}
        self.links['h2'] = {}
        self.links[1] = {}
        self.links[2] = {}
        self.links['h1'][1] = (0, 1)
        self.links['h2'][2] = (0, 3)
        self.links[1]['h1'] = (1, 0)
        self.links[2]['h2'] = (3, 0)

    def initialize_links(self, app):
        self.topo_raw_switches = copy.copy(get_switch(app, None))
        # The Function get_link(self, None) outputs the list of links.
        self.topo_raw_links = copy.copy(get_link(app, None))

        for l in self.topo_raw_links:
            link = l.to_dict()
            src = link['src']
            dst = link['dst']
            self.links[int(src['dpid'], 16)] = self.links.get(int(src['dpid'], 16), {})
            self.links[int(src['dpid'], 16)][int(dst['dpid'], 16)] = (int(src['port_no']), int(dst['port_no']))