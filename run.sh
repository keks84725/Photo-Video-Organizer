#!/bin/bash
cd "$(dirname "$0")"

# Check Python 3
if command -v python3.12 &>/dev/null; then
    PYTHON_CMD="python3.12"
elif command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
else
    echo "Python 3 is not installed. Please install Python 3.10+."
    exit 1
fi

$PYTHON_CMD main.py
