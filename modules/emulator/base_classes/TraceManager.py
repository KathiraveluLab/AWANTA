from abc import ABC, abstractmethod
from Measurement import Measurement

class TraceManager(ABC):

    def __init__(self, measurement_data):
        self.measurement_map: list[Measurement] = measurement_data

    @abstractmethod
    def get_data(self) -> Measurement:
        pass



