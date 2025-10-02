#!/bin/bash

# Assertly Test Management Platform Startup Script

echo "🚀 Starting Assertly Test Management Platform..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not available. Please install pip."
    exit 1
fi

# Create virtual environment if it doesn't exist
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

# Set default environment variables
export SECRET_KEY=${SECRET_KEY:-"dev-secret-key-change-in-production"}
export DEBUG=${DEBUG:-"True"}
export HOST=${HOST:-"0.0.0.0"}
export PORT=${PORT:-"5000"}

# Start the application
echo "🌟 Starting application on http://$HOST:$PORT"
echo "Press Ctrl+C to stop the server"
echo ""

python run.py