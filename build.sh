#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p app/file_handler/uploads
mkdir -p app/file_handler/outputs

echo "Build completed successfully!"
