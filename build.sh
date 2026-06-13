#!/bin/bash
set -e

echo "Installing Python 3.10 dependencies..."
python3.10 -m pip install --upgrade pip
python3.10 -m pip install --no-cache-dir -r requirements.txt

echo "Build completed successfully!"



