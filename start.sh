#!/bin/bash
# Start script for the LLM Function Calling FastAPI application

echo "🚀 Starting LLM Function Calling FastAPI Application..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
echo "📚 Installing/updating dependencies..."
pip install -r requirements.txt

# Create necessary directories
mkdir -p app/file_handler/uploads app/file_handler/outputs

# Start the server
echo "🌐 Starting server on http://localhost:8001..."
echo "💡 Press Ctrl+C to stop the server"
echo ""

python main.py
