from abc import ABC, abstractmethod
from NodeMeasurement import NodeMeasurement
from modules.emulator.src.trace_manager.Measurement import Measurement


class TraceManager(ABC):

    def __init__(self, path):
        self.path = path
        self.measurements: dict[str: NodeMeasurement] = {}

    @abstractmethod
    def process_files(self) -> None:
        pass
    
    @abstractmethod
    def get_next_state(self) -> list[Measurement]:
        pass

    # Create an iterator



