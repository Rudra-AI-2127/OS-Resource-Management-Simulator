#!/bin/bash
set -e
echo "Running Project Tests..."
if command -v python3 &>/dev/null; then
    python3 -m unittest discover -s tests -v
else
    python -m unittest discover -s tests -v
fi
echo "Testing Completed Successfully."
