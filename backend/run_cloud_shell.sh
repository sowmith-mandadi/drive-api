#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Setting up the backend for Cloud Shell...${NC}"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${BLUE}Detected Python version: ${PYTHON_VERSION}${NC}"

# Function to handle errors
handle_error() {
    echo -e "${RED}Error: $1${NC}"
    echo -e "${YELLOW}Attempting to continue...${NC}"
}

# Clean up any existing virtual environment
if [ -d "venv" ]; then
    echo -e "${YELLOW}Removing existing virtual environment...${NC}"
    rm -rf venv
fi

# Create a new virtual environment
echo -e "${BLUE}Creating a new virtual environment...${NC}"
python3 -m venv venv || handle_error "Failed to create virtual environment"
source venv/bin/activate || handle_error "Failed to activate virtual environment"

# Upgrade pip
echo -e "${BLUE}Upgrading pip...${NC}"
pip install --upgrade pip setuptools wheel || handle_error "Failed to upgrade pip"

# Check if running on Python 3.12+
if [[ "${PYTHON_VERSION}" == 3.12* ]] || [[ "${PYTHON_VERSION}" > 3.12 ]]; then
    echo -e "${YELLOW}Python 3.12+ detected. Installing compatible packages...${NC}"
    # Install compatible packages for Python 3.12+
    pip install "fastapi>=0.100.0,<0.116.0" "pydantic>=2.0.0,<3.0.0" "uvicorn>=0.20.0,<0.30.0" || handle_error "Failed to install core packages"

    # Create/patch config.py workaround for pydantic-settings issues
    if grep -q "pydantic_settings" app/core/config.py; then
        echo -e "${YELLOW}Patching config.py to use pydantic instead of pydantic-settings...${NC}"
        # Create backup
        cp app/core/config.py app/core/config.py.bak
        # Replace pydantic-settings with direct pydantic usage
        sed -i.bak 's/from pydantic_settings import BaseSettings/# Using direct pydantic for Python 3.12 compatibility\nfrom pydantic import BaseModel\n\n# Create a BaseSettings replacement\nclass BaseSettings(BaseModel):\n    model_config = {"extra": "ignore"}/g' app/core/config.py
        echo -e "${GREEN}Patched config.py for Python 3.12 compatibility${NC}"
    fi
else
    echo -e "${BLUE}Installing packages for Python ${PYTHON_VERSION}...${NC}"
    # For Python 3.11 and below, use original package versions
    pip install "fastapi>=0.95.0,<0.100.0" "pydantic<2.0.0" "uvicorn>=0.20.0,<0.30.0" || handle_error "Failed to install core packages"
    pip install "pydantic-settings>=2.0.0,<3.0.0" || handle_error "Failed to install pydantic-settings"
fi

# Install common packages for all Python versions
echo -e "${BLUE}Installing common dependencies...${NC}"
pip install "gunicorn>=21.0.0,<22.0.0" || handle_error "Failed to install gunicorn"
pip install "python-multipart>=0.0.6,<0.0.10" "python-dotenv>=1.0.0,<2.0.0" "starlette>=0.25.0,<0.50.0" || handle_error "Failed to install base dependencies"
pip install "itsdangerous>=2.1.2,<3.0.0" || handle_error "Failed to install itsdangerous"

# Install Google-related packages
echo -e "${BLUE}Installing Google API packages...${NC}"
pip install "firebase-admin>=6.0.0,<7.0.0" || handle_error "Failed to install firebase-admin"
pip install "google-api-python-client>=2.95.0,<3.0.0" || handle_error "Failed to install google-api-python-client"
pip install "google-auth>=2.20.0,<3.0.0" "google-auth-httplib2>=0.1.0,<0.2.0" "google-auth-oauthlib>=1.0.0,<2.0.0" || handle_error "Failed to install google-auth packages"
pip install "google-cloud-storage>=2.10.0,<3.0.0" || handle_error "Failed to install google-cloud-storage"

# Install data and ML packages
echo -e "${BLUE}Installing data processing and ML packages...${NC}"
pip install "numpy>=1.20.0,<2.0.0" "scikit-learn>=1.0.0,<2.0.0" || handle_error "Failed to install ML packages"
pip install "pandas>=1.5.0,<3.0.0" || handle_error "Failed to install pandas"

# Install utility packages
echo -e "${BLUE}Installing utility packages...${NC}"
pip install "requests>=2.30.0,<3.0.0" "structlog>=23.0.0,<24.0.0" "httpx>=0.20.0,<1.0.0" "tenacity>=8.0.0,<9.0.0" || handle_error "Failed to install utility packages"

# Document processing packages
echo -e "${BLUE}Installing document processing packages...${NC}"
pip install "pypdf2>=3.0.0,<4.0.0" || handle_error "Failed to install pypdf2"

# Create upload directories if they don't exist
echo -e "${BLUE}Creating upload directories...${NC}"
mkdir -p uploads/temp uploads/bucket || handle_error "Failed to create upload directories"

# Check environment variables
echo -e "${BLUE}Checking environment variables...${NC}"
if [ -z "$GOOGLE_CLIENT_ID" ] || [ -z "$GOOGLE_CLIENT_SECRET" ]; then
    echo -e "${YELLOW}Warning: Google API credentials not set. Some features may not work.${NC}"
    echo -e "${YELLOW}Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables.${NC}"
fi

# Final setup message
echo -e "${GREEN}Setup complete!${NC}"
echo -e "${BLUE}To run the application:${NC}"
echo -e "  ${GREEN}python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload${NC}"
echo -e "${BLUE}Or start it now by pressing Enter...${NC}"
read -p "Press Enter to start the server or Ctrl+C to exit..."

# Run the application
echo -e "${BLUE}Starting uvicorn server...${NC}"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
