#!/bin/bash
set -e
echo "Starting OS Simulator Pro-Max Native Web Server..."
if command -v python3 &>/dev/null; then
    python3 server.py "$@"
else
    python server.py "$@"
fi
