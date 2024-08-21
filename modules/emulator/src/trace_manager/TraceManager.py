from abc import ABC, abstractmethod
from .NodeMeasurement import NodeMeasurement
from .Measurement import Measurement


class TraceManager(ABC):
    """This is a base class for trace extraction strategies. Each newly implemented trace extraction strategy should inherit from this class. Each new trace extraction strategy should implement :func: `process_files` and :func: `get_next_state`

    :param path: The path to the trace results folder.
    :type path: str
    """
    def __init__(self, path):
        self.path = path
        self.measurements: dict[str: NodeMeasurement] = {}

    @abstractmethod
    def process_files(self) -> None:
        """Processes all the trace results in the folder passed into the tracemanager and stores the results into a list of measurement objects.

        :return: Does not return anything
        :rtype: None
        """
        pass
    
    @abstractmethod
    def get_next_state(self) -> list[Measurement]:
        """Provides the next set of measurements for all the nodes in the network topology as a list of measurement objects where ith measurement in the list corresponds to the measurement of ith node in the network topology.

        :return: Does not return anything
        :rtype: None
        """
        pass



