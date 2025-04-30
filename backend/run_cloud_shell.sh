#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Setting up the backend for Cloud Shell...${NC}"

# Clean up any existing virtual environment
if [ -d "venv" ]; then
    echo -e "${YELLOW}Removing existing virtual environment...${NC}"
    rm -rf venv
fi

# Create a new virtual environment
echo -e "${BLUE}Creating a new virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo -e "${BLUE}Upgrading pip...${NC}"
pip install --upgrade pip setuptools wheel

# Install compatible versions of critical packages first
echo -e "${BLUE}Installing compatible versions of critical packages...${NC}"
pip install "fastapi>=0.95.0,<0.100.0" "pydantic<2.0.0" "uvicorn>=0.20.0,<0.30.0" "gunicorn>=21.0.0,<22.0.0"
pip install "python-multipart>=0.0.6,<0.0.10" "python-dotenv>=1.0.0,<2.0.0" "starlette>=0.25.0,<0.30.0"

# Skip pydantic-settings which has compatibility issues with Python 3.12
echo -e "${YELLOW}Skipping pydantic-settings (replaced in code)...${NC}"

# Install other requirements
echo -e "${BLUE}Installing remaining requirements...${NC}"
pip install "firebase-admin>=6.0.0,<7.0.0"
pip install "google-api-python-client>=2.95.0,<3.0.0"
pip install "google-auth>=2.20.0,<3.0.0"
pip install "google-auth-httplib2>=0.1.0,<0.2.0"
pip install "google-auth-oauthlib>=1.0.0,<2.0.0"
pip install "numpy>=1.20.0,<2.0.0" "scikit-learn>=1.0.0,<2.0.0"
pip install "requests>=2.30.0,<3.0.0" "structlog>=23.0.0,<24.0.0" "httpx>=0.20.0,<1.0.0"

# Create upload directories if they don't exist
echo -e "${BLUE}Creating upload directories...${NC}"
mkdir -p uploads/temp uploads/bucket

# Check if config.py was modified
if grep -q "BaseModel" app/core/config.py; then
    echo -e "${GREEN}config.py already updated to use standard pydantic.${NC}"
else
    echo -e "${RED}Warning: config.py may not be updated. Run the backend and check for errors.${NC}"
fi

# Run the application
echo -e "${GREEN}Setup complete! Running the application...${NC}"
echo -e "${BLUE}Starting uvicorn server...${NC}"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
