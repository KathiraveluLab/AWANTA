from __future__ import annotations

import json
import logging
import os

from .Measurement import Measurement
from .NodeMeasurement import NodeMeasurement
from .TraceManager import TraceManager
from ..utils.utils import file_splitter

class CustomLatencyExtractor(TraceManager):
    """This is a custom latency extractor that extracts latency from the trace results. Note that the trace results must be ogranized in a certain way to utilize this strategy.

    :param path: The path to the trace measurements.
    :type path: str
    """
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
                    measurements.append(Measurement(int(key), m))
                node_measurement = NodeMeasurement(key, measurements)
                self.measurements[key] = iter(node_measurement)
        except IOError as e:
            logging.error("Error in accessing measurement files")

    def get_next_state(self) -> list[Measurement] | None:
        measurements: list[Measurement] = []
        try:
            for dpid, node_measurements in self.measurements.items():
                measurements.append(next(node_measurements.measurement_iterator))
            return measurements

        except StopIteration:
            return None
