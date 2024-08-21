<div align="center">
  <img src="images/AWANTA.png" alt="Project Header">
</div>

<div align="center">
  <h1>AWANTA SDN Emulator</h1>
</div>

[//]: # ([![PyPI]&#40;https://badge.fury.io/py/tensorflow.svg&#41;]&#40;https://badge.fury.io/py/tensorflow&#41;)
[//]: # ([![Github - Build]&#40;https://github.com/scrapinghub/dateparser/workflows/Build/badge.svg&#41;]&#40;https://github.com/scrapinghub/dateparser/actions&#41;)

[//]: # ([![Python]&#40;https://img.shields.io/pypi/pyversions/tensorflow.svg&#41;]&#40;https://badge.fury.io/py/tensorflow&#41;)

[//]: # ([![Contributor Covenant]&#40;https://img.shields.io/badge/Contributor%20Covenant-v1.4%20adopted-ff69b4.svg&#41;]&#40;CODE_OF_CONDUCT.md&#41;)

[//]: # ([![Code Coverage]&#40;https://codecov.io/gh/scrapinghub/dateparser/branch/master/graph/badge.svg&#41;]&#40;https://codecov.io/gh/scrapinghub/dateparser&#41;)

[//]: # ([![docs]&#40;https://readthedocs.org/projects/dateparser/badge/?version=latest&#41;]&#40;https://dateparser.readthedocs.org/en/latest/?badge=latest&#41;)

This project provides an emulator designed to simulate a small, fully connected mesh network with n nodes. The primary purpose of this emulator is to demonstrate and analyze network path changes under varying conditions.
Our emulator performs a trace-driven simulation, leveraging real-world latency data obtained from RIPE Atlas nodes. By injecting these latency traces during iperf tests conducted between the start and destination nodes, we can replicate realistic network conditions and observe the effects on performance.



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
$ sudo python run_topology.py -topo <custom_topology_class>
```

### Custom Topology

For example, create a custom mininet topology class under network_manager/custom_topologies and register it under a name of your choice under network_manager/custom_topologies/__init__.py in the topology_map variable.

For an illustration a full_mesh_topology class has been created and is used by default when no topology is given in the command line interface.
```
$ sudo python3 -topo full_mesh_topology
```
Please do note that mininet requires sudo access, so when running these commands, don't forget to use sudo.

## Running the Ryu Controller

To start the ryu controller, install the ryu package from pip or build it from source. And run the controller file.

```
$ ryu-manager --observe-links modules/emulator/controller.py
```

The controller has a configuration file ```controller.conf```, which contains the trace_manager to use and the routing strategy to use. These variables are passed through the .conf file because ryu controller does not allow command line arguments in the shell.


