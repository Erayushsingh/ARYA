#!/bin/bash
# Railway startup script for ARYA

echo "🚀 Starting ARYA deployment setup..."

# Create necessary directories
mkdir -p app/file_handler/uploads
mkdir -p app/file_handler/outputs

echo "📁 Directories created"

# Install Python dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "📦 Dependencies installed"

# Start the application
echo "🌟 Starting ARYA server..."
python -m uvicorn main:app --host 0.0.0.0 --port $PORT
