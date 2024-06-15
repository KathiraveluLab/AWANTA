from mininet.topo import Topo

class NetworkTopology(Topo):
    def __init__( self ):
        # Initialize topology
        Topo.__init__( self )
        # Add hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        # Add switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        # Add links
        self.addLink(h1,s1)
        self.addLink(h2,s1)
        self.addLink(h1,s2)
        self.addLink(h2,s2)

topos = { 'network_topology': (lambda: NetworkTopology())}