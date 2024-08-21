****************************
Network Manager
****************************


The network manager module is responsible for extracting information about the topology links and ports at startup. This information is useful at the time of adding and removing flows between mininet nodes.

Custom Topologies
^^^^^^^^^^^^^^^^^^^^^

The custom topologies are implemented as a sub module under the network manager module. These custom topologies are utilized by the mininet script at startup to build the skeleton of the required network topology. We can implement our own topology by following the mininet custom topology guidelines here - https://mininet.org/walkthrough/#custom-topologies.

For example below is the custom full mesh topology script utilized as default:


.. code-block:: python

    class FullMeshTopology(Topo):
    """This class is a custom topology class for full mesh topology. You can create your own custom topology by following the mininet custom topology tutorial here - https://mininet.org/walkthrough/#custom-topologies.

    """
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



.. https://mininet.org/walkthrough/#custom-topologies: https://mininet.org/walkthrough/#custom-topologies


Module
^^^^^^^

.. toctree::
    :maxdepth: 2

    ../src.network_manager.rst

