# Sintra
**S**elf-adaptive **I**nter-domain **N**etwork **T**ransfers for **Ra**diology.

Sintra performs inter-domain network transfers for radiology, in a network-aware manner.


# Sintra Components

## measurements-client

Sintra Measurements Client is based on [RIPE Atlas](https://atlas.ripe.net/) and RIPE Atlas Tools. It assumes existing RIPE Atlas credits acquired by hosting a probe locally or through credits transfer from someone who has accumulated some credits themselves. Then [configure the RIPE Atlas Tools](https://ripe-atlas-tools.readthedocs.io/en/latest/use.html#configuration), which is a Python-based library. The Sintra Measurements Client builds on top of the RIPE Atlas. 

## controller

Sintra Software-Defined Wide Area Network (SD-WAN) Controller builds on top of Ryu.

## scheduler

Sintra scheduler is a decentralized scheduler in all the Sintra nodes.

## viseu

Viseu (Virtual Internet Services at the Edge) is a peer-to-peer overlay that enables users to join the decentralized framework of Sintra.
