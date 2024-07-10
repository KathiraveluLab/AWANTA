import json
import os
from constants import TraceManagerConstants
from utils import file_splitter
import logging


class TraceManager:

    def __init__(self, path):
        self.path = path
        self.measurement_files = os.listdir(self.path)
        self.latency_data = dict()

    def process_files(self):
        try:
            for file in self.measurement_files:
                key = file_splitter(file)
                abs_path = os.path.join(self.path, file)
                with open(abs_path) as measurement:
                    data = json.load(measurement)
                self.latency_data[key] = data
        except IOError as e:
            logging.error("Error in accessing measurement files")

        return self.latency_data
