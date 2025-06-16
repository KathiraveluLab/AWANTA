# An SD-WAN framework for telehealth access

**AWANTA (A**daptive Software-Defined **W**ide **A**rea **N**etwork framework for **T**elehealth **A**ccess) performs inter-domain network transfers for telehealth, in a network latency-aware manner.


# Modules

## measurements-client

The Measurements Client is based on [RIPE Atlas](https://atlas.ripe.net/) and RIPE Atlas Tools. It assumes existing RIPE Atlas credits acquired by hosting a probe locally or through credits transfer from someone who has accumulated some credits themselves. Then [configure the RIPE Atlas Tools](https://ripe-atlas-tools.readthedocs.io/en/latest/use.html#configuration), which is a Python-based library. The Measurements Client builds on top of the RIPE Atlas. 

## cloud-router

A decentralized cloud router in all the client nodes.

## event-manager

Propagates the changes in measurements as events to a broker.

## controller

The Software-Defined Wide Area Network (SD-WAN) Controller builds on top of Ryu.


# Citing AWANTA

If you use AWANTA in your research, please cite the below paper:
* Caballero, E. S., Ramirez, J., Alisetti, S. V., Almario, S., and Kathiravelu, P. Network Measurements for Telehealth Optimizations. Understanding Internet Paths in Remote Regions. In Cluster Computing – The Journal of Networks Software Tools and Applications (CLUSTER). (IF: 2.7, Q1). June 2025. Springer. https://doi.org/10.1007/s10586-024-05069-z
  
* Kathiravelu, P., Bhimireddy, A., and Gichoya, J. Network Measurements and Optimizations for Telehealth in Internet's Remote Regions. In the Tenth IEEE International Conference on Software Defined Systems (SDS-2023). pp. 39-46, October 2023. https://doi.org/10.1109/SDS59856.2023.10329044.
