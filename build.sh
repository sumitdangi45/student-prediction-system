#!/bin/bash
set -e

echo "Installing dependencies..."
pip install --upgrade pip

# Install with no cache to force fresh download
pip install --no-cache-dir -r requirements.txt

echo "Build completed successfully!"


