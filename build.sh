#!/bin/bash
set -e

# Force Python 3.10
export PYTHON_VERSION=3.10.13

# Clear any cached environments
rm -rf /opt/render/project/src/.venv

# Install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt --only-binary :all:

echo "Build completed successfully!"
