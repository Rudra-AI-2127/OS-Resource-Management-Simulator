#!/bin/bash
set -e
echo "Starting OS Simulator..."
if command -v python3 &>/dev/null; then
    python3 main.py "$@"
else
    python main.py "$@"
fi
