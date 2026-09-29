from .full_mesh_topology import FullMeshTopology
from .ring_topology import RingTopology

topology_map = {
    "full_mesh_topology": FullMeshTopology(),
    "ring_topology": RingTopology(),
}