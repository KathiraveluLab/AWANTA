# Mininet Emulator

This emulator is designed to emulate a small 3 node network to show path changes in the network. Here we perform a trace driven simulation by taking latency measurements from RIPE Atlas nodes and injecting the traces during an iperf test from start node to destination node.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Mininet
- Ryu SDN Controller
- Python 3.7+

### Installation

- Mininet

> Download Mininet Framework
```
Follow this quickstart guide
http://mininet.org/download/
```

> Python Drivers
```
$ pip install mininet
```

- Ryu SDN
```
Follow the installation setup here
https://ryu-sdn.org/
```

- Python 3.7+
```
Download python 3.7+ binaries from here
https://www.python.org/downloads/
```

## Trace Driven Emulator (high level design)
![Trace Driven Emulation.png](images%2FTrace%20Driven%20Emulation.png)

## Running the Mininet Emulator

To run with the given topology, please run this command.
```
$ sudo mn --custom modules/emulator/topology.py --topo network_topology
```

Or run the topology file directly
```
$ sudo python3 modules/emulator/topology.py
```
Please do note that mininet requires sudo access, so when running these commands, don't forget to use sudo.

## Running the Ryu Controller

To start the ryu controller, install the ryu package from pip or build it from source. And run the controller file.

```
$ ryu-manager --observe-links modules/emulator/controller.py
```

## Topology Design

![Network Topology.png](images%2FNetwork%20Topology.png)​



## Trace Driven Simulation Results

We utilize RIPE ATLAS trace results from the measurement module and integrate it with the SDN Framework. The SDN Framework dynamically switches the path based on these latency metrics. These experiments are yet to be done.


