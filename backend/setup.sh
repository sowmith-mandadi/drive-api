#!/bin/bash

# FastAPI backend setup script

# Exit on error
set -e

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp ../.env.example .env
    echo "Please update the .env file with your settings."
fi

# Create necessary directories
mkdir -p uploads

echo "FastAPI backend setup complete!"
echo "To run the application, use: uvicorn main:app --reload" 