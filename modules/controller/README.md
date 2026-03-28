# AWANTA SD-WAN Controller

The AWANTA SD-WAN Controller is a Ryu-based SDN application responsible for global path optimization and flow scheduling.

## Features
- Real-time event subscription for network measurements.
- Adaptive path calculation using the Latency Relaxing algorithm.
- Dynamic flow installation on OpenFlow switches.

This component integrates with the `awanta.events` queue to react to changing network conditions.