#!/bin/bash

echo "========================================"
echo "   SAGE Medical AI Review Tool"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "ERROR: Python is not installed"
    echo "Please install Python from https://python.org"
    exit 1
fi

# Use python3 if available, otherwise python
if command -v python3 &> /dev/null; then
    PYTHON=python3
    PIP=pip3
else
    PYTHON=python
    PIP=pip
fi

echo "Using Python: $($PYTHON --version)"
echo

echo "Installing required packages..."
$PIP install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install requirements"
    echo "Please check your internet connection and try again"
    exit 1
fi

echo
echo "Starting SAGE Web Interface..."
echo
echo "========================================"
echo "   Access the tool at:"
echo "   http://localhost:5001"
echo "   Password: djhwu"
echo "========================================"
echo
echo "Press Ctrl+C to stop the server"
echo

$PYTHON app.py