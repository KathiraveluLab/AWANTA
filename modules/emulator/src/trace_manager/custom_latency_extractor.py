import json
import logging
import os

from modules.emulator.src.trace_manager.Measurement import Measurement
from modules.emulator.src.trace_manager.NodeMeasurement import NodeMeasurement
from modules.emulator.src.trace_manager.TraceManager import TraceManager
from modules.emulator.src.utils.utils import file_splitter

"""
This extractor requires the latency data in the following format:
1.json
2.json
3.json
...

where 1.json represents the latency data of packets from node 1. The json format is as follows:
[
{
    2: float,
    3: float,
    ...
    n: float
},
{
    2: float,
    3: float,
    ....,
    n: float
}
]

Here this is format in 1.json. Each object in the array signifies the result in a timestep. Also the key, value in each object signify the destination node and the latency value from node 1.
"""


class CustomLatencyExtractor(TraceManager):
    def __init__(self, path):
        super().__init__(path)

    def process_files(self):
        try:
            measurement_files = os.listdir(self.path)
            for file in measurement_files:
                key = file_splitter(file)
                abs_path = os.path.join(self.path, file)
                with open(abs_path) as measurement:
                    data = json.load(measurement)
                measurements: list[Measurement] = []
                for m in data:
                    measurements.append(Measurement(key, m))
                node_measurement = NodeMeasurement(key, measurements)
                self.measurements[key] = iter(node_measurement)
        except IOError as e:
            logging.error("Error in accessing measurement files")

    def get_next_state(self) -> list[Measurement]:
        measurements: list[Measurement] = []
        for dpid, node_measurements in self.measurements.items():
            measurements.append(next(node_measurements.measurement_list))
        return measurements
