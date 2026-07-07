#!/bin/bash
set -e

echo "========================================="
echo "  NotebookLM Portal - Project Setup"
echo "========================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

# Setup backend
echo ""
echo "Setting up backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Created virtual environment"
else
    echo "Virtual environment already exists"
fi

# Activate and install dependencies
source venv/bin/activate
pip install -r requirements.txt -q
echo "Installed backend dependencies"

# Copy .env if not exists
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env from .env.example"
    echo "Please update .env with your configuration"
else
    echo ".env file already exists"
fi

cd ..

# Check Docker
if command -v docker &> /dev/null; then
    echo ""
    echo "Docker detected. Starting services..."
    cd docker
    docker compose -f docker-compose.dev.yml up -d postgres
    echo "Waiting for PostgreSQL..."
    sleep 5
    cd ..
else
    echo ""
    echo "Docker not found. Please install Docker or run PostgreSQL manually."
fi

echo ""
echo "========================================="
echo "  Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Update backend/.env with your settings"
echo "  2. Run 'make dev' to start the server"
echo "  3. Visit http://localhost:8000/docs for API docs"
