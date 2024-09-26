==========
Overview
==========


Getting Started
================

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

Prerequisites
==============

- Mininet
- Ryu SDN Controller
- Python 3.7+

Installation
=============

- Mininet


.. code-block:: none
    :caption: Download the Mininet Framework

    Follow this quickstart guide - http://mininet.org/download/

.. http://mininet.org/download/: http://mininet.org/download/

.. code-block:: bash
    :caption: Python Drivers

    $ pip install mininet



- Ryu SDN

.. code-block:: none
    :caption: Download Ryu SDN

    Follow this installation setup - https://ryu-sdn.org/

.. https://ryu-sdn.org/: https://ryu-sdn.org/


- Python 3.7+

.. code-block:: none

    Download python 3.7+ binaries from here - https://www.python.org/downloads/



.. https://www.python.org/downloads/: https://www.python.org/downloads/


Running the Mininet Emulator
==============================

To run with the given topology, please run this command.

.. code-block:: bash

    $ sudo python run_topology.py -topo <custom_topology_class>


Custom Topology
----------------------

For example, create a custom mininet topology class under network_manager/custom_topologies and register it under a name of your choice under network_manager/custom_topologies/__init__.py in the topology_map variable.

For an illustration a full_mesh_topology class has been created and is used by default when no topology is given in the command line interface.

.. code-block:: bash

    $ sudo python3 -topo full_mesh_topology

Please do note that mininet requires sudo access, so when running these commands, don't forget to use sudo.

Running the Ryu Controller
==============================

To start the ryu controller, install the ryu package from pip or build it from source. And run the controller file.


.. code-block:: bash

    $ ryu-manager --observe-links modules/emulator/controller.py


The controller has a configuration file ``controller.conf``, which contains the trace_manager to use and the routing strategy to use. These variables are passed through the .conf file because ryu controller does not allow command line arguments in the shell.


