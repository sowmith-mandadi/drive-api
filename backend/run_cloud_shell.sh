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

# Function to install package with verification
install_with_verify() {
    package_spec=$1
    package_name=$(echo $1 | cut -d'>' -f1 | cut -d'<' -f1 | cut -d'=' -f1)
    
    echo -e "${BLUE}Installing $package_name...${NC}"
    pip install $package_spec

    # Verify the installation
    if ! pip show $package_name > /dev/null 2>&1; then
        echo -e "${RED}Failed to install $package_name. Trying again with no version constraint...${NC}"
        pip install $package_name
        
        if ! pip show $package_name > /dev/null 2>&1; then
            echo -e "${RED}Installation of $package_name still failed. This may cause issues.${NC}"
            return 1
        fi
    fi
    
    echo -e "${GREEN}Successfully installed $package_name${NC}"
    return 0
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
    install_with_verify "fastapi>=0.100.0,<0.116.0" 
    install_with_verify "pydantic>=2.0.0,<3.0.0"
    install_with_verify "uvicorn>=0.20.0,<0.30.0"
    
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
    install_with_verify "fastapi>=0.95.0,<0.100.0"
    install_with_verify "pydantic<2.0.0"
    install_with_verify "uvicorn>=0.20.0,<0.30.0"
    install_with_verify "pydantic-settings>=2.0.0,<3.0.0"
fi

# Install common packages for all Python versions
echo -e "${BLUE}Installing common dependencies...${NC}"
install_with_verify "gunicorn>=21.0.0,<22.0.0"
install_with_verify "python-multipart>=0.0.6,<0.0.10"
install_with_verify "python-dotenv>=1.0.0,<2.0.0"
install_with_verify "starlette>=0.25.0,<0.50.0"

# Special handling for itsdangerous
echo -e "${YELLOW}Installing itsdangerous (required for session middleware)...${NC}"
pip uninstall -y itsdangerous
install_with_verify "itsdangerous>=2.0.0" || {
    echo -e "${RED}First attempt to install itsdangerous failed. Trying alternative installation...${NC}"
    pip install itsdangerous --no-cache-dir
    
    if ! pip show itsdangerous > /dev/null 2>&1; then
        echo -e "${RED}Installation of itsdangerous still failed. Installing specific version...${NC}"
        pip install itsdangerous==2.1.2
    fi
}

# Install Google-related packages
echo -e "${BLUE}Installing Google API packages...${NC}"
install_with_verify "firebase-admin>=6.0.0,<7.0.0"
install_with_verify "google-api-python-client>=2.95.0,<3.0.0"
install_with_verify "google-auth>=2.20.0,<3.0.0"
install_with_verify "google-auth-httplib2>=0.1.0,<0.2.0"
install_with_verify "google-auth-oauthlib>=1.0.0,<2.0.0"
install_with_verify "google-cloud-storage>=2.10.0,<3.0.0"
install_with_verify "google-cloud-tasks>=2.13.0,<3.0.0"

# Install data and ML packages
echo -e "${BLUE}Installing data processing and ML packages...${NC}"
install_with_verify "numpy>=1.20.0,<2.0.0"
install_with_verify "scikit-learn>=1.0.0,<2.0.0"
install_with_verify "pandas>=1.5.0,<3.0.0"

# Install utility packages
echo -e "${BLUE}Installing utility packages...${NC}"
install_with_verify "requests>=2.30.0,<3.0.0"
install_with_verify "structlog>=23.0.0,<24.0.0"
install_with_verify "httpx>=0.20.0,<1.0.0"
install_with_verify "tenacity>=8.0.0,<9.0.0"

# Document processing packages
echo -e "${BLUE}Installing document processing packages...${NC}"
install_with_verify "pypdf2>=3.0.0,<4.0.0"

# Create upload directories if they don't exist
echo -e "${BLUE}Creating upload directories...${NC}"
mkdir -p uploads/temp uploads/bucket || handle_error "Failed to create upload directories"

# Handle missing OAuth credentials
echo -e "${BLUE}Checking for OAuth credentials...${NC}"
if [ -z "$GOOGLE_CLIENT_ID" ] || [ -z "$GOOGLE_CLIENT_SECRET" ]; then
    echo -e "${YELLOW}Google OAuth credentials not found. Creating stub implementation...${NC}"
    
    # Create a task_service_stub.py file to bypass Google Cloud Tasks import error
    cat > app/services/task_service_stub.py << 'EOF'
"""
Stub implementation of TaskService to use when Cloud Tasks is not available.
"""
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TaskService:
    """Stub implementation of TaskService that logs instead of creating real tasks."""
    
    def __init__(self):
        logger.warning("Using TaskService stub implementation - Cloud Tasks not available")
        self.tasks = []
    
    def create_task(self, queue_name, endpoint, payload, delay_seconds=0):
        """Log the task instead of creating it in Cloud Tasks."""
        scheduled_time = datetime.now() + timedelta(seconds=delay_seconds)
        task_id = f"stub-task-{len(self.tasks)+1}"
        
        logger.info(
            f"STUB TASK CREATED - ID: {task_id}, "
            f"Queue: {queue_name}, "
            f"Endpoint: {endpoint}, "
            f"Scheduled: {scheduled_time}, "
            f"Payload size: {len(str(payload))} bytes"
        )
        
        self.tasks.append({
            "id": task_id,
            "queue": queue_name,
            "endpoint": endpoint,
            "scheduled_time": scheduled_time,
            "payload": payload,
        })
        
        return task_id
EOF

    # Update imports in files that use TaskService
    if [ -f "app/api/endpoints/batch.py" ]; then
        echo -e "${YELLOW}Patching batch.py to use stub implementation...${NC}"
        cp app/api/endpoints/batch.py app/api/endpoints/batch.py.bak
        
        # Use sed to replace the import
        sed -i.bak "s/from app.services.task_service import TaskService/# Using stub implementation\nfrom app.services.task_service_stub import TaskService/g" app/api/endpoints/batch.py
        echo -e "${GREEN}Patched batch.py${NC}"
    fi
    
    echo -e "${YELLOW}Created stub implementation for Cloud Tasks. The app will log tasks instead of creating them.${NC}"
    echo -e "${YELLOW}For actual functionality, set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables.${NC}"
fi

# Verify critical packages are installed
echo -e "${BLUE}Verifying critical packages...${NC}"
missing_packages=()

for pkg in "fastapi" "uvicorn" "pydantic" "starlette" "itsdangerous"; do
    if ! pip show $pkg > /dev/null 2>&1; then
        missing_packages+=($pkg)
    fi
done

if [ ${#missing_packages[@]} -ne 0 ]; then
    echo -e "${RED}Critical packages still missing: ${missing_packages[*]}${NC}"
    echo -e "${YELLOW}Attempting emergency installation of missing packages...${NC}"
    
    for pkg in "${missing_packages[@]}"; do
        echo -e "${BLUE}Emergency installation of $pkg...${NC}"
        pip install $pkg --no-cache-dir
    done
fi

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
