import pathlib
package_root = pathlib.Path(__file__).parent.parent.parent.resolve()

class TraceManagerConstants:
    PATH = str(package_root) + "/modules/emulator/measurements/"
    DELIMITER = "."
    EXTENSION = "json"

class NetworkManagerConstants:
    SRC = "src"
    DST = "dst"
    PORT_NO = "port_no"
    DP_ID = "dpid"

class MininetConstants:
    SRC_IP = "10.0.0.1"
    DST_IP = "10.0.0.2"
    SRC_HOST = "h1"
    DST_HOST = "h2"
    NUM_FULL_MESH = 3
    SWITCHES = "s"
    SRC_SWITCH = "s0"
    DST_SWITCH = f"s{NUM_FULL_MESH - 1}"
    CONTROLLER_IP = "0.0.0.0"
    CONTROLLER_PORT = 6633
    CONTROLLER_LABEL = "c"
    INFO = "info"
    SRC_SWITCH_LABEL = 0
    DST_SWITCH_LABEL = NUM_FULL_MESH - 1


class RoutingConstants:
    pass

class ControllerConstants:
    FLOW_PRIORITY = 2
    FREQUENCY = 10

