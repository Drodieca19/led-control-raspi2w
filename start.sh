#!/bin/bash

# RPi Zero 2W LED Controller - Startup Script
# This script handles virtual environment creation, dependency installation,
# and starts the Flask web GUI dashboard with appropriate root permissions.

# Exit immediately if any command fails
set -e

# Define variables
VENV_DIR=".venv"
REQUIREMENTS_FILE="requirements.txt"
APP_FILE="app.py"

echo "=== RPi Zero 2W LED Controller Dashboard ==="

# 1. Verify python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed on this system." >&2
    exit 1
fi

# 2. Check and initialize virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in '$VENV_DIR'..."
    # Attempt to create virtual env.
    if ! python3 -m venv "$VENV_DIR"; then
        echo "" >&2
        echo "Error: Failed to create virtual environment." >&2
        echo "This usually happens because 'python3-venv' is missing in DietPi/Debian." >&2
        echo "Please install it by running:" >&2
        echo "    sudo apt update && sudo apt install -y python3-venv" >&2
        echo "" >&2
        exit 1
    fi
fi

# 3. Activate virtual environment and install dependencies
echo "Activating virtual environment..."
source "$VENV_DIR"/bin/activate

echo "Ensuring dependencies are up to date..."
pip install --upgrade pip
pip install -r "$REQUIREMENTS_FILE"

# 4. Execute the web application using sudo on the venv python executable
echo "Starting Flask Web GUI..."
echo "To control hardware LED nodes, root permissions are required."
echo "Running: sudo '$VENV_DIR/bin/python' '$APP_FILE'"
echo "--------------------------------------------------------"

# Using the explicit path to the virtual env python executable under sudo
# guarantees that we run with root privileges while still loading Flask dependencies.
sudo "$VENV_DIR"/bin/python "$APP_FILE"
