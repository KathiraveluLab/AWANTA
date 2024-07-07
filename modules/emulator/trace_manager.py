import json


class TraceManager:

    def __init__(self, path):
        self.path = path


    def process_files(self):
        with open("measurements/s1.json") as s1_m:
            s1_data = json.load(s1_m)

        with open("measurements/s2.json") as s2_m:
            s2_data = json.load(s2_m)

        with open("measurements/s12.json") as s12_m:
            s12_data = json.load(s12_m)

        return {1: s1_data, 12: s12_data, 2: s2_data}