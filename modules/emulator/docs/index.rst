.. AWANTA SDN Emulator documentation master file, created by
   sphinx-quickstart on Mon Aug 19 11:15:14 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to AWANTA SDN Emulator's documentation!
==================================================================

This project provides an emulator designed to simulate a small, fully connected mesh network with n nodes. The primary purpose of this emulator is to demonstrate and analyze network path changes under varying conditions.
Our emulator performs a trace-driven simulation, leveraging real-world latency data obtained from RIPE Atlas nodes. By injecting these latency traces during iperf tests conducted between the start and destination nodes, we can replicate realistic network conditions and observe the effects on performance.


The Emulator
--------------

.. image:: ../images/FullMeshTopology.png



.. toctree::
   :maxdepth: 3



   overview/overview.rst
   design.rst

   emulation/emulation.rst
