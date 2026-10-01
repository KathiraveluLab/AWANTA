from mininet.topo import Topo
from ...utils.constants import MininetConstants


class RingTopology(Topo):
    """
    Custom topology where switches are connected in a ring: each switch
    links only to its immediate neighbors, plus one link closing the ring
    from the last switch back to the first.

    This exists because FullMeshTopology gives every switch a direct link
    to every other switch, so a direct route is always available and
    multi-hop routing strategies (see modules/cloud_router/src/routing)
    never actually have to find a real multi-hop path. In a ring, only
    neighbor-to-neighbor links exist, so genuinely different paths (going
    one way around the ring versus the other) exist between distant
    switches, giving those strategies something real to route across.

    IMPORTANT LIMITATION: a ring needs more than 3 switches to be
    meaningfully different from FullMeshTopology (a 3-node ring is a
    triangle, identical to a 3-node full mesh). This class supports any
    num_switches, but NetworkManager and controller.py currently hardcode
    which switch the source/destination hosts attach to
    (MininetConstants.SRC_SWITCH_LABEL / DST_SWITCH_LABEL), independent of
    which topology is actually running. Those are still tied to
    NUM_FULL_MESH, so running this topology with a different switch count
    and expecting the live controller/routing pipeline to compute correct
    routes end-to-end requires making those labels topology-aware first,
    which is out of scope for this change. This class can be constructed,
    inspected, and validated on its own (its structure is exactly what a
    ring should be), but full live integration is a separate follow-up.
    """

    def __init__(self, num_switches: int = 5):
        Topo.__init__(self)

        self.src_ip = MininetConstants.SRC_IP
        self.dst_ip = MininetConstants.DST_IP
        self.num_switches = num_switches
        self.switch_map = dict()

        source_host = self.addHost(MininetConstants.SRC_HOST, ip=self.src_ip)
        destination_host = self.addHost(MininetConstants.DST_HOST, ip=self.dst_ip)

        for i in range(num_switches):
            switch_name = MininetConstants.SWITCHES + str(i + 1)
            self.switch_map[switch_name] = self.addSwitch(switch_name)

        # Ring links: each switch to its next neighbor, wrapping the last
        # switch back around to the first to close the cycle.
        for i in range(num_switches):
            current_name = MininetConstants.SWITCHES + str(i + 1)
            next_name = MininetConstants.SWITCHES + str((i + 1) % num_switches + 1)
            self.addLink(self.switch_map[current_name], self.switch_map[next_name])

        # Hosts attach to the first and last switch in the ring, mirroring
        # FullMeshTopology's convention of source at the first switch and
        # destination at the last.
        first_switch = MininetConstants.SWITCHES + "1"
        last_switch = MininetConstants.SWITCHES + str(num_switches)
        self.addLink(source_host, self.switch_map[first_switch])
        self.addLink(destination_host, self.switch_map[last_switch])