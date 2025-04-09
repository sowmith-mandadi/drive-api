#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Setting up the FastAPI backend environment...${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3 and try again.${NC}"
    exit 1
fi

# Check if virtualenv is installed
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}pip3 is not installed. Please install pip3 and try again.${NC}"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
pip install -r requirements.txt

# Set up pre-commit hooks
echo -e "${BLUE}Setting up pre-commit hooks...${NC}"
pre-commit install

echo -e "${GREEN}Setup complete. Activate the environment with 'source venv/bin/activate'${NC}"
echo -e "${GREEN}Start the server with 'uvicorn main:app --reload'${NC}"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${BLUE}Creating .env file from .env.example...${NC}"
    if [ -f "../.env.example" ]; then
        cp ../.env.example .env
        echo -e "${GREEN}.env file created. Please update with your configuration.${NC}"
    else
        echo -e "${RED}.env.example not found. Please create a .env file manually.${NC}"
    fi
fi

# Create necessary directories
mkdir -p uploads

echo "FastAPI backend setup complete!"
echo "To run the application, use: uvicorn main:app --reload"
