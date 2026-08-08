#!/bin/bash
# run_awanta.sh - Orchestrates a full AWANTA run: starts the Ryu controller
# in the background, then launches the Mininet topology in the foreground
# (which needs sudo and gives you the interactive Mininet CLI). On exit,
# automatically tears down the controller and cleans up leftover Mininet
# state, so you don't have to manage two terminals and remember cleanup
# by hand every time.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"
CONTROLLER_LOG="$SCRIPT_DIR/controller.log"

TOPOLOGY="full_mesh_topology"
TRACE_MANAGER="custom_latency_extractor"
ROUTING="latency_relaxing"

usage() {
    echo "Usage: ./run_awanta.sh [-topo TOPOLOGY] [-trace TRACE_MANAGER] [-routing ROUTING]"
    echo ""
    echo "  -topo     Topology class to run (default: full_mesh_topology)"
    echo "  -trace    Trace manager strategy: custom_latency_extractor | event_trace_manager (default: custom_latency_extractor)"
    echo "  -routing  Routing strategy (default: latency_relaxing)"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -topo) TOPOLOGY="$2"; shift 2 ;;
        -trace) TRACE_MANAGER="$2"; shift 2 ;;
        -routing) ROUTING="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) echo "Unknown argument: $1"; usage ;;
    esac
done

if [ ! -x "$VENV_PYTHON" ]; then
    echo "Error: virtual environment not found at $SCRIPT_DIR/.venv"
    echo "Run ./setup_env.sh first."
    exit 1
fi

CONTROLLER_PID=""

cleanup() {
    echo ""
    echo "Shutting down AWANTA..."
    if [ -n "$CONTROLLER_PID" ] && kill -0 "$CONTROLLER_PID" 2>/dev/null; then
        echo "  Stopping Ryu controller (PID $CONTROLLER_PID)..."
        kill "$CONTROLLER_PID" 2>/dev/null || true
        wait "$CONTROLLER_PID" 2>/dev/null || true
    fi
    echo "  Cleaning up Mininet state..."
    sudo mn -c > /dev/null 2>&1 || true
    echo "Done."
}
trap cleanup EXIT INT TERM

echo "Cleaning up any leftover Mininet state from a previous run..."
sudo mn -c > /dev/null 2>&1 || true

echo "Starting Ryu controller (trace_manager=$TRACE_MANAGER, routing=$ROUTING)..."
echo "  Logs: $CONTROLLER_LOG"
"$SCRIPT_DIR/.venv/bin/ryu-manager" --observe-links \
    --trace_manager="$TRACE_MANAGER" --routing="$ROUTING" \
    "$SCRIPT_DIR/modules/emulator/controller.py" > "$CONTROLLER_LOG" 2>&1 &
CONTROLLER_PID=$!

sleep 2
if ! kill -0 "$CONTROLLER_PID" 2>/dev/null; then
    echo "Error: Ryu controller failed to start. Check $CONTROLLER_LOG for details."
    exit 1
fi
echo "  Controller running (PID $CONTROLLER_PID)"

echo "Starting Mininet topology '$TOPOLOGY' (requires sudo)..."
echo "  Type 'exit' in the Mininet CLI when you're done to shut everything down cleanly."
echo ""
sudo "$VENV_PYTHON" "$SCRIPT_DIR/modules/emulator/run_topology.py" -topo "$TOPOLOGY"