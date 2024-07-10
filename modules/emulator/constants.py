import pathlib
package_root = pathlib.Path(__file__).parent.parent.parent.resolve()

class TraceManagerConstants:
    PATH = str(package_root) + "/modules/emulator/measurements/"
    DELIMITER = "."
    EXTENSION = "json"

class NetworkManagerConstants:
    SRC = "src"
    DST = "dst"