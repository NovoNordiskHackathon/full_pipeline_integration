#!/bin/bash

# Start the Enhanced PTD Generator Flask application
echo "🚀 Starting Enhanced PTD Generator Flask application..."
echo ""
echo "✨ Features:"
echo "   • Complete document processing pipeline (DOC/PDF → JSON → PTD)"
echo "   • Adobe PDF Services integration"
echo "   • Template-based PTD generation"
echo "   • Real-time progress tracking"
echo ""
echo "🌐 Backend: http://127.0.0.1:5000"
echo "🖥️  Frontend: Open frontend/index.html in your browser"
echo ""
echo "📋 Optional: Set Adobe PDF Services credentials for full functionality:"
echo "   export PDF_SERVICES_CLIENT_ID=your_client_id"
echo "   export PDF_SERVICES_CLIENT_SECRET=your_client_secret"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Change to the script directory
cd "$(dirname "$0")"

# Start the Flask app
python3 app.py