# Trace Driven Emulator

This project provides an emulator designed to simulate a small, fully connected mesh network with n nodes. The primary purpose of this emulator is to demonstrate and analyze network path changes under varying conditions.

Our emulator performs a trace-driven simulation, leveraging real-world latency data obtained from RIPE Atlas nodes. By injecting these latency traces during iperf tests conducted between the start and destination nodes, we can replicate realistic network conditions and observe the effects on performance.

![Full Mesh Topology.png](images%2FFull%20Mesh%20Topology.png)







## The Emulator

### Modules

![Trace Driven Emulation.png](images%2FTrace%20Driven%20Emulation.png)



### Activity

![Low Level.png](images%2FLow%20Level.png)

- **Periodic Process Loop**
  - **Controller**: The controller spawns the periodic thread, that is responsible for initiating the process loop.
  - **Trace Manager**: The trace manager fetches the next measurement required from the trace results data file.
  - **Network Manager**: The network manager fetches the link state topology from the mininet emulator, and constructs a virtual graph network.
  - **Routing Manager**: The routing manager is responsible for creating a optimal route path from the given virtual topology and the network measurements from the trace manager. The routing manager passes the optimal route path to the controller, where the controller sets these paths between the given path nodes using open flow protocol.







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


