from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import RemoteController, CPULimitedHost
import argparse
from src.utils.constants import MininetConstants
from src.network_manager.custom_topologies import topology_map

def run(args):
    c = RemoteController(MininetConstants.CONTROLLER_LABEL, MininetConstants.CONTROLLER_IP, MininetConstants.CONTROLLER_PORT)
    topo = topology_map[args.topology]
    net = Mininet(topo=topo, host=CPULimitedHost, controller=None)
    net.addController(c)
    net.start()

    CLI(net)
    net.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Mininet Emulator',
        description='Initializes the network topology to be run inside the mininet framework')

    parser.add_argument('-topo', '--topology', type=str, default="full_mesh_topology", help="Custom Topology Class Qualifier")
    args = parser.parse_args()
    setLogLevel(MininetConstants.INFO)
    run(args)
