from mininet.topo import Topo

class NetworkTopology(Topo):
    def __init__( self ):
        # Initialize topology
        Topo.__init__( self )
        # Add hosts
        h1 = self.addHost('origin')

        h2 = self.addHost('intermediate_node1')
        h3 = self.addHost('intermediate_node2')
        h4 = self.addHost('destination')

        # Add links
        self.addLink(h1, h2)
        self.addLink(h1, h3)
        self.addLink(h4, h3)
        self.addLink(h4, h2)

topos = { 'network_topology': (lambda: NetworkTopology())}