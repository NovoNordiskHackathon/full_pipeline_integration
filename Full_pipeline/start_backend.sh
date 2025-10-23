#!/bin/bash

# PTD Generator Backend Startup Script (rebuilt)
set -euo pipefail

echo "🚀 Starting PTD Generator Backend..."

if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ Python 3 is required but not installed." >&2
  exit 1
fi

# Use project-local venv
if [ ! -d "venv" ]; then
  echo "📦 Creating virtual environment..."
  python3 -m venv venv
fi

# shellcheck disable=SC1091
source venv/bin/activate

# Install dependencies (ensure Flask + CORS present)
echo "📥 Installing dependencies..."
pip install -r requirements.txt >/dev/null 2>&1 || true
pip install flask>=2.3.0 flask-cors>=4.0.0 werkzeug>=2.3.0

# Ensure backend folders (uploads/output live under backend now)
mkdir -p backend/uploads backend/output

# Start Flask server
echo "🌐 Starting Flask server on http://localhost:5000"
python backend/app.py
