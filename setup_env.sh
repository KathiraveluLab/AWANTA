#!/bin/bash
# setup_env.sh - Automates AWANTA Python environment setup and patches legacy Ryu
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[1/4] Installing standard requirements..."
pip install --upgrade pip
pip install wheel
pip install -r "$SCRIPT_DIR/requirements.txt"

# ryu (the SDN framework used by the emulator/controller) is an old package
# whose setup script relies on a setuptools API that newer setuptools
# releases removed, so an older setuptools must be pinned right before
# installing it, and nothing should be installed after this point that
# could pull in a newer setuptools again (e.g. via pbr).
echo "[2/4] Pinning setuptools to a version compatible with legacy ryu packaging..."
pip install "setuptools==58.0.4"

echo "[3/4] Installing ryu (bypassing pip build isolation)..."
pip install "ryu==4.34" --no-build-isolation --no-cache-dir

echo "[4/4] Patching ryu for compatibility with modern oslo/eventlet..."
python "$SCRIPT_DIR/scripts/patch_ryu.py"

# setuptools was intentionally downgraded earlier to install ryu's legacy
# build, but ryu itself doesn't need setuptools at runtime once installed.
# Restore a modern setuptools so the rest of the environment isn't left on
# a 2021-era version, which could break other packages or future installs.
echo "Restoring a modern setuptools now that ryu is installed..."
pip install --upgrade setuptools

echo "Setup complete! You can now run the AWANTA components."