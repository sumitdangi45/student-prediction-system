#!/bin/bash
set -e

echo "Building with pip..."
pip install --upgrade pip
pip install --only-binary :all: -r requirements.txt

echo "Build completed successfully!"

