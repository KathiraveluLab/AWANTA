from constants import TraceManagerConstants, MininetConstants
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

def preprocess_ids(dpids: list[str]) -> list[str]:

    for i in range(len(dpids)):
        if dpids[i] == MininetConstants.SRC_HOST or dpids[i] == MininetConstants.DST_HOST:
            continue
        else:
            dpids[i] = MininetConstants.SWITCHES + str(dpids[i])

    return dpids