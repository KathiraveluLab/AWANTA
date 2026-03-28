# AWANTA Measurements Client

The AWANTA Measurements Client performs network measurements based on the RIPE Atlas framework. It is a core component of the AWANTA framework for adaptive SDN-based telehealth access.

## Running the AWANTA Measurements Client

To start the client, run:
```bash
python3 MeasurementsClient.py
```
This will start the AWANTA Measurements Client and begin a periodic measurement cycle.

The output will be stored in `output/awanta.out` for logs and `output/awanta_measurements` for results.
Real-time events are propagated to the SD-WAN controller via the Event Manager (ActiveMQ/STOMP).