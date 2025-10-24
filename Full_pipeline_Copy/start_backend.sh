#!/bin/bash

# PTD Generator Backend Startup Script

echo "🚀 Starting PTD Generator Backend..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads output

# Start the Flask server
echo "🌐 Starting Flask server on http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""
# Prefer the fully wired backend that performs real generation
python apptest.py