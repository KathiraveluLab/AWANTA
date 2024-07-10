from constants import TraceManagerConstants
from exceptions import ExtensionError


def file_splitter(file_name: str) -> str:

    data = file_name.split(TraceManagerConstants.DELIMITER)
    filename = data[0]
    extension = data[1]

    if extension == TraceManagerConstants.EXTENSION:
        return filename
    else:
        raise ExtensionError

def convert_dpid_key(dpid: str) -> int:
    return int(dpid, 16)