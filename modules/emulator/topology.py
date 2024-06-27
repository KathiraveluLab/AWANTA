from logging import info

from mininet.cli import CLI
from mininet.net import Mininet
from mininet.node import RemoteController, CPULimitedHost
from mininet.topo import Topo

class NetworkTopology(Topo):
    def __init__( self ):
        # Initialize topology
        Topo.__init__( self )

        self.src_ip = '10.0.0.1'
        self.dst_ip = '10.0.0.2'

        # Add hosts
        alaska_host = self.addHost('h1', ip=self.src_ip)
        newyork_host = self.addHost('h2', ip=self.dst_ip)

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


def installStaticFlows(net, topo):
    print(net.links)
    for sw in net.switches:
        print(type(sw.ports.keys()[0]), "here")
        info('Adding flows to %s...' % sw.name)
        sw.dpctl('add-flow', "ip,nw_src={},nw_dst={},actions=output:2".format(topo.src_ip, topo.dst_ip))
        # sw.dpctl('add-flow', 'in_port=1,actions=output:3')
        # sw.dpctl('add-flow', 'in_port=2,actions=output=1')
        # sw.
        info(sw.dpctl('dump-flows'))


def run():
    c = RemoteController('c', '0.0.0.0', 6633)
    topo = NetworkTopology()
    net = Mininet(topo=topo, host=CPULimitedHost, controller=None)
    net.addController(c)
    net.start()

    installStaticFlows(net, topo)
    CLI(net)
    net.stop()



if __name__ == "__main__":
    run()


