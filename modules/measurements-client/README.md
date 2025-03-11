# Sintra Measurements Client

Sintra Measurements Client is a python-based toolkit that performs periodic Internet measurements based on RIPE Atlas.


# Configuring the Sintra Measurements Client

Sintra Measurements Client performs the measurements based on the RIPE Atlas Client.

Find the config.json file in the folder and modify accordingly.

* *Target*: The target that is set to receive the data from the probes.

* *NoOfProbes*: Maximum is 500 per iteration. You may leave this value as-is.

* *From*: An array of nations to send data from. By default, adds all the nations.

* *Measure*: Measurement. For latency, leave it as the default value, "ping".

* *Me*: Set your or your probe's IP address. 


# Running the Sintra Measurements Client
## For Linux
Run the following command to start the measurements client:

```bash
$ nohup python3 MeasurementsClient.py
```


## For Windows
On Windows, you can use the following command to run the client:

```bash
$ start python MeasurementsClient.py
```
This will start the Sintra Measurements Client in a new command prompt window. 

The output will be stored in `sintra.out`.