#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Setting up the FastAPI backend environment...${NC}"

# Function to check if command exists
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}$1 is not installed. Please install $1 and try again.${NC}"
        return 1
    fi
    return 0
}

# Check if Python is installed
if ! check_command python3; then
    exit 1
fi

# Check if pip is installed
if ! check_command pip3; then
    echo -e "${YELLOW}Attempting to install pip...${NC}"
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install pip. Please install pip3 manually and try again.${NC}"
        exit 1
    fi
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo -e "${BLUE}Detected Python version: ${PYTHON_VERSION}${NC}"

# Determine if we should use a specific Python version
if [[ "$PYTHON_VERSION" == "3.12" ]]; then
    echo -e "${YELLOW}Python 3.12 detected. Some packages may have compatibility issues.${NC}"
    echo -e "${YELLOW}Checking for Python 3.9 or 3.10...${NC}"
    
    if command -v python3.9 &> /dev/null; then
        echo -e "${GREEN}Python 3.9 found. Using Python 3.9 for compatibility.${NC}"
        PYTHON_CMD="python3.9"
    elif command -v python3.10 &> /dev/null; then
        echo -e "${GREEN}Python 3.10 found. Using Python 3.10 for compatibility.${NC}"
        PYTHON_CMD="python3.10"
    else
        echo -e "${YELLOW}Compatible Python version not found. Using current version but some packages may fail.${NC}"
        PYTHON_CMD="python3"
    fi
else
    PYTHON_CMD="python3"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment with $PYTHON_CMD...${NC}"
    $PYTHON_CMD -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create virtual environment. Trying alternative method...${NC}"
        check_command pip3
        pip3 install virtualenv
        virtualenv venv
        if [ $? -ne 0 ]; then
            echo -e "${RED}Failed to create virtual environment. Please check your Python installation.${NC}"
            exit 1
        fi
    fi
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to activate virtual environment. Please check if the directory exists.${NC}"
    exit 1
fi

# Upgrade pip and essential tools
echo -e "${BLUE}Upgrading pip and essential tools...${NC}"
pip install --upgrade pip setuptools wheel

# Check for Cloud Shell environment
if [ -d "/google/devshell" ] || [ -n "$CLOUD_SHELL" ]; then
    echo -e "${YELLOW}Cloud Shell environment detected. Using compatibility settings.${NC}"
    # Install compatible versions of libraries for Cloud Shell
    echo -e "${BLUE}Installing compatible packages for Cloud Shell...${NC}"
    pip install "fastapi<0.100.0" "pydantic<2.0.0" "uvicorn>=0.20.0,<0.30.0" "gunicorn>=21.0.0,<22.0.0"
    
    # Install the rest of requirements but skip pydantic which we already installed
    echo -e "${BLUE}Installing remaining dependencies...${NC}"
    grep -v "pydantic" requirements.txt | grep -v "fastapi" | grep -v "uvicorn" | grep -v "gunicorn" > temp_requirements.txt
    pip install -r temp_requirements.txt
    rm temp_requirements.txt
else
    # Install dependencies normally
    echo -e "${BLUE}Installing dependencies...${NC}"
    pip install -r requirements.txt
    
    # Handle potential pydantic issues
    if pip list | grep -q "pydantic" && ! python -c "import pydantic_core" &> /dev/null; then
        echo -e "${YELLOW}pydantic_core issue detected. Fixing...${NC}"
        pip uninstall -y pydantic pydantic-core
        pip install "pydantic<2.0.0"
    fi
fi

# Set up pre-commit hooks if available
if check_command pre-commit; then
    echo -e "${BLUE}Setting up pre-commit hooks...${NC}"
    pre-commit install
else
    echo -e "${YELLOW}pre-commit not available. Skipping hooks setup.${NC}"
    pip install pre-commit
    pre-commit install
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${BLUE}Creating .env file from .env.example...${NC}"
    if [ -f "../.env.example" ]; then
        cp ../.env.example .env
        echo -e "${GREEN}.env file created. Please update with your configuration.${NC}"
    elif [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}.env file created. Please update with your configuration.${NC}"
    else
        echo -e "${YELLOW}.env.example not found. Creating a basic .env file.${NC}"
        cat > .env << EOF
# Basic environment configuration
# Update with your values
GOOGLE_CLIENT_ID="YOUR_CLIENT_ID"
GOOGLE_CLIENT_SECRET="YOUR_CLIENT_SECRET"
GOOGLE_REDIRECT_URI="http://localhost:8000/api/auth/callback"
FRONTEND_URL="http://localhost:4200"
SESSION_SECRET_KEY="development_secret_key"
EOF
        echo -e "${GREEN}Basic .env file created. Please update with your configuration.${NC}"
    fi
fi

# Create necessary directories
mkdir -p uploads/temp uploads/bucket

# Test the installation
echo -e "${BLUE}Testing installation...${NC}"
if python -c "import fastapi, uvicorn, pydantic" &> /dev/null; then
    echo -e "${GREEN}Core packages imported successfully.${NC}"
else
    echo -e "${RED}There may be issues with the installation. Please check the error messages.${NC}"
fi

echo -e "${GREEN}FastAPI backend setup complete!${NC}"
echo -e "${GREEN}To activate the environment: ${BLUE}source venv/bin/activate${NC}"
echo -e "${GREEN}To run the application: ${BLUE}uvicorn main:app --reload${NC}"
echo -e "${GREEN}For deployment info: ${BLUE}cat README.md | grep -A 20 'Deployment'${NC}"
