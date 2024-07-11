from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import RemoteController, CPULimitedHost
from mininet.topo import Topo
from constants import MininetConstants


class NetworkTopology(Topo):
    def __init__(self):
        # Initialize topology
        Topo.__init__(self)

        self.src_ip = MininetConstants.SRC_IP
        self.dst_ip = MininetConstants.DST_IP

        self.switch_map = dict()

        # Add hosts
        source_host = self.addHost(MininetConstants.SRC_HOST, ip=self.src_ip)
        destination_host = self.addHost(MininetConstants.DST_HOST, ip=self.dst_ip)

        # Add Switches
        for i in range(MininetConstants.NUM_FULL_MESH):
            self.switch_map[MininetConstants.SWITCHES + str(i+1)] = self.addSwitch(MininetConstants.SWITCHES + str(i+1))

        # Add Full Mesh Links
        for i in range(MininetConstants.NUM_FULL_MESH):
            for j in range(i + 1, MininetConstants.NUM_FULL_MESH):
                self.addLink(self.switch_map[MininetConstants.SWITCHES + str(i+1)], self.switch_map[MininetConstants.SWITCHES + str(j+1)])

        # Host Links
        self.addLink(source_host, self.switch_map[MininetConstants.SRC_SWITCH])
        self.addLink(destination_host, self.switch_map[MininetConstants.DST_SWITCH])


def run():
    c = RemoteController(MininetConstants.CONTROLLER_LABEL, MininetConstants.CONTROLLER_IP, MininetConstants.CONTROLLER_PORT)
    topo = NetworkTopology()
    net = Mininet(topo=topo, host=CPULimitedHost, controller=None)
    net.addController(c)
    net.start()

    CLI(net)
    net.stop()


if __name__ == "__main__":
    setLogLevel(MininetConstants.INFO)
    run()
