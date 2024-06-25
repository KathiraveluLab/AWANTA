from logging import info

from mininet.cli import CLI
from mininet.net import Mininet
from mininet.node import RemoteController, CPULimitedHost
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

# topos = { 'network_topology': (lambda: NetworkTopology())}


def installStaticFlows(net):
    print(net.links)
    for sw in net.switches:
        print(sw.ports, "here")
        info('Adding flows to %s...' % sw.name)
        sw.dpctl('add-flow', 'in_port=1,actions=output:2')
        # sw.dpctl('add-flow', 'in_port=2,actions=output=1')
        info(sw.dpctl('dump-flows'))


def run():
    c = RemoteController('c', '0.0.0.0', 6633)
    net = Mininet(topo=NetworkTopology(), host=CPULimitedHost, controller=None)
    net.addController(c)
    net.start()

    installStaticFlows(net)
    CLI(net)
    net.stop()



if __name__ == "__main__":
    run()


