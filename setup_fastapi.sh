#!/bin/bash
# Setup script for FastAPI backend

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "backend/fast_venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv backend/fast_venv
fi

# Activate virtual environment
source backend/fast_venv/bin/activate

# Install requirements
echo "Installing FastAPI dependencies..."
pip install fastapi uvicorn starlette

# Install additional dependencies from requirements.txt
if [ -f "backend/fast_backend/requirements.txt" ]; then
    echo "Installing additional dependencies from requirements.txt..."
    pip install -r backend/fast_backend/requirements.txt
fi

echo "FastAPI setup complete!"
echo "To run the FastAPI server, use: python run_api.py"
echo "For the full server version, use: python run_api.py --type server"
echo "API documentation will be available at: http://localhost:8000/docs" 