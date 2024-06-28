# Mininet Emulator

This emulator is designed to emulate a small 3 node network to show path changes in the network. Here we perform a trace driven simulation by taking latency measurements from RIPE Atlas nodes and injecting the traces during an iperf test from start node to destination node.


## Installation


## Running Mininet

To run with the given topology, please run this command.
> sudo mn --custom modules/emulator/topology.py --topo network_topology

Or run the topology file directly
> python topology.py


## Running Ryu Controller

To start the ryu controller, install the ryu package from pip or build it from source. And run the controller file.

> ryu-manager controller.py

## Topology Design

![Network Topology.png](images%2FNetwork%20Topology.png)

