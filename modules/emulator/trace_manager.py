import json
import os
from constants import TraceManagerConstants
from utils import file_splitter


class TraceManager:

    def __init__(self, path):
        self.path = path
        self.measurement_files = os.listdir(self.path)
        self.latency_data = dict()

    def process_files(self):

        for file in self.measurement_files:
            key = file_splitter(file)
            abs_path = os.path.join(self.path, file)
            with open(abs_path) as measurement:
                data = json.load(measurement)
            self.latency_data[key] = data

        return self.latency_data