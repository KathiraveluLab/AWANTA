from mininet.cli import CLI
from mininet.log import setLogLevel
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
        self.addLink(newyork_host, newyork_switch)


def run():
    c = RemoteController('c', '0.0.0.0', 6633)
    topo = NetworkTopology()
    net = Mininet(topo=topo, host=CPULimitedHost, controller=None)
    net.addController(c)
    net.start()

    CLI(net)
    net.stop()



if __name__ == "__main__":
    setLogLevel('info')
    run()


