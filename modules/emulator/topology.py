from mininet.topo import Topo

class NetworkTopology(Topo):
    def __init__( self ):
        # Initialize topology
        Topo.__init__( self )

        # Add hosts
        alaska_host = self.addHost('h1')
        newyork_host = self.addHost('h2')

        # Add Switches
        alaska_switch = self.addSwitch('s1')
        seattle_switch = self.addSwitch('s12')
        newyork_switch = self.addSwitch('s2')


        # Add links
        self.addLink(alaska_host, alaska_switch)
        self.addLink(alaska_switch, seattle_switch)
        self.addLink(seattle_switch, newyork_switch)
        self.addLink(alaska_switch, newyork_switch)
        self.addLink(newyork_switch, newyork_host)

topos = { 'network_topology': (lambda: NetworkTopology())}