#!/bin/bash

# Quick start script for EverMemOS Memory Server

echo "🚀 Starting EverMemOS Memory Server..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "📋 Copying .env.example to .env..."
    cp .env.example .env
    echo "✅ Please edit .env file and set your EVERMEMOS_API_KEY"
    echo ""
fi

# Check if dependencies are installed
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    echo ""
fi

# Start the server
echo "🔌 Starting server on http://localhost:8000"
echo "📖 API docs available at http://localhost:8000/docs"
echo ""
python3 main.py
