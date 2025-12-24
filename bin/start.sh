#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Get the project root (parent of bin/)
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_ROOT"

echo "🎴 Pokemon Sleeve Collection Manager"
echo "===================================="
echo ""
echo "Starting server with auto-processing features..."
echo "Once started, open your browser to: http://localhost:5005"
echo "Gallery view available at: http://localhost:5005/gallery"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

export ADMIN_PASSWORD=Pokemon2015
python src/app.py
