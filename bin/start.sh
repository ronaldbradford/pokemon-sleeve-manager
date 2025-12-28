#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Get the project root (parent of bin/)
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$PROJECT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Using venv..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Load environment variables if .envrc exists
if [ -f .envrc ]; then
    source .envrc
fi

# Set default port if not set
export PORT=${PORT:-5005}

echo "🎴 Pokemon Sleeve Collection Manager"
echo "===================================="
echo ""
echo "Starting server with auto-processing features..."
echo "Once started, open your browser to: http://localhost:${PORT}"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run Flask app
python -m app.main
