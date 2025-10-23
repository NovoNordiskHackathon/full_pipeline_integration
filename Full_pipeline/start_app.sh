#!/bin/bash

# Start the PTD Generator Flask application
echo "Starting PTD Generator Flask application..."
echo "Backend will be available at: http://127.0.0.1:5000"
echo "Frontend: Open frontend/index.html in your browser"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Change to the script directory
cd "$(dirname "$0")"

# Start the Flask app
python3 app.py