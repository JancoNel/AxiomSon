#!/bin/bash
# AxiomSon auto-setup and launch script for Linux/macOS

echo ""
echo "========================================"
echo "AxiomSon - Auto Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH."
    echo "Please install Python 3.8+ from https://www.python.org"
    echo "Or use your package manager:"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-venv"
    echo "  macOS: brew install python3"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "[1/3] Creating virtual environment..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment."
        exit 1
    fi
fi

# Activate virtual environment
echo "[2/3] Activating virtual environment..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment."
    exit 1
fi

# Install requirements
echo "[3/3] Installing dependencies from requirements.txt..."
pip install -r requirements.txt -q
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies."
    echo "Try running: pip install -r requirements.txt"
    exit 1
fi

echo ""
echo "========================================"
echo "Setup complete! Launching Sound codewar..."
echo "========================================"
echo ""

# Launch the application
python alpha.py --gui

# Display exit code if there's an error
if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Application exited with an error."
fi
