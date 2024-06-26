# Mininet Emulator

This emulator is designed to emulate a small 3 node network to show path changes in the network. Here we perform a trace driven simulation by taking latency measurements from RIPE Atlas nodes and injecting the traces during an iperf test from start node to destination node.

![Network Topology.png](images%2FNetwork%20Topology.png)



## Running with Custom Topology

To run with the given topology, please run this command.
> sudo mn --custom modules/emulator/topology.py --topo network_topology

## Topology Design