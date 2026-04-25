#!/bin/bash
# setup_env.sh - Automates AWANTA Python environment setup and patches legacy Ryu

set -e

echo "[1/4] Installing standard requirements..."
pip install -r requirements.txt

echo "[2/4] Installing ryu dependencies (wheel, setuptools workaround)..."
pip install wheel
pip install "setuptools==67.6.1"

echo "[3/4] Installing ryu (bypassing pip build isolation)..."
pip install ryu --no-build-isolation

echo "[4/4] Patching ryu for modern eventlet compatibility..."
python -c "
import os
import ryu.app.wsgi as w
file_path = w.__file__

with open(file_path, 'r') as f:
    content = f.read()

# Replace ALREADY_HANDLED logic
content = content.replace('from eventlet.wsgi import ALREADY_HANDLED', '# from eventlet.wsgi import ALREADY_HANDLED')
content = content.replace('_ALREADY_HANDLED = ALREADY_HANDLED', '# _ALREADY_HANDLED = ALREADY_HANDLED')
content = content.replace('return self._ALREADY_HANDLED', 'return []')

with open(file_path, 'w') as f:
    f.write(content)
print(f'Successfully patched {file_path}')
"

echo "Setup complete! You can now run the AWANTA components."
