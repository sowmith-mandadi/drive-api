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

# Process command line arguments
RECREATE_VENV=false  # Default to false to keep venv for speed
SKIP_DEPS=true      # Default to true to skip deps for speed
QUICK_START=true    # Default to true to start quickly
ADD_DEBUG=true      # Default to true to add debug logs

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --recreate-venv)
      RECREATE_VENV=true
      shift
      ;;
    --install-deps)
      SKIP_DEPS=false
      shift
      ;;
    --full-setup)
      RECREATE_VENV=true
      SKIP_DEPS=false
      QUICK_START=false
      shift
      ;;
    --no-debug)
      ADD_DEBUG=false
      shift
      ;;
    *)
      echo -e "${YELLOW}Unknown option: $1${NC}"
      shift
      ;;
  esac
done

# Function to handle errors
handle_error() {
    echo -e "${RED}Error: $1${NC}"
    echo -e "${YELLOW}Attempting to continue...${NC}"
}

# Function to check if package is already installed
package_installed() {
    package_name=$1
    if pip list | grep -F "$package_name" > /dev/null 2>&1; then
        return 0  # package installed
    else
        return 1  # package not installed
    fi
}

# Function to install package with verification
install_with_verify() {
    package_spec=$1
    package_name=$(echo $1 | cut -d'>' -f1 | cut -d'<' -f1 | cut -d'=' -f1)
    
    # Check if package is already installed
    if package_installed "$package_name"; then
        echo -e "${GREEN}Package $package_name already installed. Skipping.${NC}"
        return 0
    fi

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

# Manage virtual environment
if [ "$RECREATE_VENV" = true ]; then
    # Clean up any existing virtual environment
    if [ -d "venv" ]; then
        echo -e "${YELLOW}Removing existing virtual environment...${NC}"
        rm -rf venv
    fi

    # Create a new virtual environment
    echo -e "${BLUE}Creating a new virtual environment...${NC}"
    python3 -m venv venv || handle_error "Failed to create virtual environment"
else
    if [ -d "venv" ]; then
        echo -e "${GREEN}Using existing virtual environment...${NC}"
    else
        echo -e "${YELLOW}No existing virtual environment found. Creating a new one...${NC}"
        python3 -m venv venv || handle_error "Failed to create virtual environment"
    fi
fi

source venv/bin/activate || handle_error "Failed to activate virtual environment"

# Set Google Cloud credential environment variables (do this regardless of SKIP_DEPS)
echo -e "${BLUE}Setting up Google Cloud credentials...${NC}"
if [ -f "credentials.json" ]; then
    echo -e "${GREEN}Found credentials.json file. Setting up environment variables...${NC}"
    export GOOGLE_APPLICATION_CREDENTIALS="credentials.json"
    export GOOGLE_SERVICE_ACCOUNT_PATH="credentials.json"
    export USE_GCS="true"
    export DEBUG="true"
    
    # TESTING DIFFERENT COLLECTION NAMES
    export FIRESTORE_COLLECTION_CONTENT="content"  # Try capitalized version
    echo -e "${YELLOW}TESTING ENVIRONMENT VARIABLE: FIRESTORE_COLLECTION_CONTENT=${FIRESTORE_COLLECTION_CONTENT}${NC}"
    
    # Try to extract the service account email
    if command -v python &> /dev/null; then
        SERVICE_EMAIL=$(python -c "import json; f=open('$GOOGLE_APPLICATION_CREDENTIALS'); data=json.load(f); print(f'Service account email: {data.get(\"client_email\", \"unknown\")}')")
        echo -e "${GREEN}$SERVICE_EMAIL${NC}"
    else
        echo -e "${YELLOW}Python not available to extract service account email.${NC}"
    fi
else
    echo -e "${YELLOW}Warning: credentials.json file not found. Some features may not work.${NC}"
    echo -e "${YELLOW}The application will use default or stub implementations where possible.${NC}"
fi

# Add debugging for empty API response issue
if [ "$ADD_DEBUG" = true ]; then
    echo -e "${BLUE}Adding debug code to fix empty API response issue...${NC}"

    # Make a backup of the content repository file
    if [ -f "app/repositories/content_repository.py" ]; then
        cp app/repositories/content_repository.py app/repositories/content_repository.py.bak
    fi
    
    # Add a test endpoint to app/api/endpoints/content.py to check Firestore access
    if [ -f "app/api/endpoints/content.py" ]; then
        cp app/api/endpoints/content.py app/api/endpoints/content.py.bak
        
        # Add a test endpoint to try different collection names
        cat > /tmp/test_endpoint.py << 'EOF'

@router.get("/test-firestore", response_model=Dict[str, Any])
async def test_firestore():
    """Test Firestore connection and collection access."""
    from app.db.firestore_client import FirestoreClient
    from app.core.config import settings
    import datetime
    import uuid
    import traceback
    
    result = {
        "success": False,
        "collections": [],
        "test_write": False,
        "errors": []
    }
    
    try:
        # Initialize client
        firestore = FirestoreClient()
        result["client_initialized"] = True
        
        # Get settings
        result["project_id"] = settings.FIRESTORE_PROJECT_ID
        result["collection"] = settings.FIRESTORE_COLLECTION_CONTENT
        
        # List collections
        collections = firestore.db.collections()
        for col in collections:
            result["collections"].append(col.id)
            
        # Try to read from content collection 
        collection = settings.FIRESTORE_COLLECTION_CONTENT
        docs = list(firestore.db.collection(collection).limit(5).stream())
        result["documents_found"] = len(docs)
        
        # If no documents, try to create a test one
        if len(docs) == 0:
            # Try a different capitalization
            alt_collection = "Content" if collection == "content" else "content"
            alt_docs = list(firestore.db.collection(alt_collection).limit(5).stream())
            result["alt_documents_found"] = len(alt_docs)
            result["alt_collection"] = alt_collection
            
            # Create a test document
            test_id = f"test-{uuid.uuid4()}"
            test_data = {
                "title": "Test Document",
                "description": "Created for testing Firestore access",
                "content_type": "test",
                "created_at": datetime.datetime.now().isoformat(),
                "updated_at": datetime.datetime.now().isoformat()
            }
            
            # Try to write to both collections
            try:
                firestore.db.collection(collection).document(test_id).set(test_data)
                result["test_write"] = True
                result["test_write_collection"] = collection
                result["test_document_id"] = test_id
            except Exception as write_err:
                result["errors"].append(f"Write error: {str(write_err)}")
                # Try alternate collection
                try:
                    firestore.db.collection(alt_collection).document(test_id).set(test_data)
                    result["test_write"] = True
                    result["test_write_collection"] = alt_collection
                    result["test_document_id"] = test_id
                except Exception as alt_write_err:
                    result["errors"].append(f"Alt write error: {str(alt_write_err)}")
        
        result["success"] = True
    except Exception as e:
        result["errors"].append(f"Error: {str(e)}")
        result["traceback"] = traceback.format_exc()
        
    return result
EOF

        # Append the test endpoint to the content.py file
        cat /tmp/test_endpoint.py >> app/api/endpoints/content.py
        echo -e "${GREEN}Added test Firestore endpoint to content.py${NC}"
    fi
    
    # Create a simple test script to add test data to Firestore
    cat > test_firestore.py << 'EOF'
#!/usr/bin/env python
"""
Test script to check Firestore access and add test data.
"""
import os
import sys
import json
import datetime
import uuid
from google.cloud import firestore

# Print environment info
print(f"GOOGLE_APPLICATION_CREDENTIALS: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')}")
print(f"FIRESTORE_COLLECTION_CONTENT: {os.environ.get('FIRESTORE_COLLECTION_CONTENT', 'content')}")

try:
    # Initialize Firestore
    db = firestore.Client()
    print("Successfully connected to Firestore")
    
    # List collections
    collections = db.collections()
    print("Collections:")
    for collection in collections:
        print(f"- {collection.id}")
        # Count documents
        docs = list(collection.limit(5).stream())
        print(f"  - Documents: {len(docs)}")
        if docs:
            # Print a sample document
            sample = docs[0].to_dict()
            sample_id = docs[0].id
            print(f"  - Sample document ID: {sample_id}")
            print(f"  - Sample fields: {list(sample.keys())[:5]}")
    
    # Create a test document in both 'content' and 'Content' collections
    collections_to_try = ['content', 'Content']
    test_id = f"test-{uuid.uuid4()}"
    test_data = {
        "title": "Test Document",
        "description": "Created for testing Firestore access",
        "content_type": "test",
        "created_at": datetime.datetime.now().isoformat(),
        "updated_at": datetime.datetime.now().isoformat()
    }
    
    print("\nAttempting to create test documents:")
    for collection in collections_to_try:
        try:
            db.collection(collection).document(test_id).set(test_data)
            print(f"Successfully created document in '{collection}' with ID: {test_id}")
        except Exception as e:
            print(f"Error creating document in '{collection}': {str(e)}")
    
    print("\nTest completed successfully")
    
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

    chmod +x test_firestore.py
    echo -e "${GREEN}Created test_firestore.py script${NC}"
    echo -e "${YELLOW}You can run it with: python test_firestore.py${NC}"
fi

# Check if dependencies should be skipped
if [ "$SKIP_DEPS" = true ]; then
    echo -e "${YELLOW}Skipping dependency installation as requested.${NC}"
else
    # Upgrade pip
    echo -e "${BLUE}Checking pip version...${NC}"
    pip --version
    pip install --upgrade pip setuptools wheel || handle_error "Failed to upgrade pip"

    # Check if running on Python 3.12+
    if [[ "${PYTHON_VERSION}" == 3.12* ]] || [[ "${PYTHON_VERSION}" > 3.12 ]]; then
        echo -e "${YELLOW}Python 3.12+ detected. Installing compatible packages...${NC}"
        # Install compatible packages for Python 3.12+
        install_with_verify "fastapi>=0.100.0,<0.116.0"
        install_with_verify "pydantic>=2.0.0,<3.0.0"
        install_with_verify "uvicorn>=0.20.0,<0.35.0"

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
    if ! package_installed "itsdangerous"; then
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
    else
        echo -e "${GREEN}itsdangerous already installed. Skipping.${NC}"
    fi

    # Install Google-related packages if not already installed
    echo -e "${BLUE}Checking Google API packages...${NC}"
    install_with_verify "firebase-admin>=6.0.0,<7.0.0"
    install_with_verify "google-api-python-client>=2.95.0,<3.0.0"
    install_with_verify "google-auth>=2.20.0,<3.0.0"
    install_with_verify "google-auth-httplib2>=0.1.0,<0.2.0"
    install_with_verify "google-auth-oauthlib>=1.0.0,<2.0.0"
    install_with_verify "google-cloud-storage>=2.10.0,<3.0.0"
    install_with_verify "google-cloud-tasks>=2.13.0,<3.0.0"

    # Install data and ML packages if not already installed
    echo -e "${BLUE}Checking data processing and ML packages...${NC}"
    install_with_verify "numpy>=1.20.0,<2.0.0"
    install_with_verify "scikit-learn>=1.0.0,<2.0.0"
    install_with_verify "pandas>=1.5.0,<3.0.0"
    install_with_verify "openpyxl>=3.1.0,<4.0.0"
    install_with_verify "xlrd>=2.0.0,<3.0.0"

    # Install document processing packages if not already installed
    echo -e "${BLUE}Checking document processing packages...${NC}"
    install_with_verify "pypdf2>=3.0.0,<4.0.0"
    echo -e "${YELLOW}Checking python-pptx (required for PowerPoint processing)...${NC}"
    install_with_verify "python-pptx>=0.6.21"

    # Install utility packages if not already installed
    echo -e "${BLUE}Checking utility packages...${NC}"
    install_with_verify "requests>=2.30.0,<3.0.0"
    install_with_verify "structlog>=23.0.0,<24.0.0"
    install_with_verify "httpx>=0.20.0,<1.0.0"
    install_with_verify "tenacity>=8.0.0,<9.0.0"

    # Install AI/LLM packages if not already installed
    echo -e "${BLUE}Checking AI/LLM packages...${NC}"
    install_with_verify "openai>=0.27.0,<1.0.0"
    install_with_verify "tiktoken>=0.4.0,<1.0.0"

    # Create stub implementation for pptx if installation failed
    if ! pip show python-pptx > /dev/null 2>&1; then
        echo -e "${YELLOW}Creating stub implementation for python-pptx...${NC}"

        # Create directory if it doesn't exist
        mkdir -p app/services/stubs

        # Create the stub file
        cat > app/services/stubs/pptx_stub.py << 'EOF'
"""
Stub implementation for python-pptx for environments where it cannot be installed.
This provides just enough functionality to prevent import errors.
"""
import logging

logger = logging.getLogger(__name__)

class Presentation:
    """Stub Presentation class that logs instead of processing PowerPoint files."""

    def __init__(self, pptx_path=None):
        self.pptx_path = pptx_path
        self.slides = []
        logger.warning(f"STUB: Created fake Presentation for {pptx_path}")

    def save(self, path):
        logger.warning(f"STUB: Pretending to save presentation to {path}")
        return True

# Create the stub for the extraction service
class PPTXExtractor:
    """Stub extractor that returns placeholder text instead of real content."""

    def extract_text(self, file_path):
        logger.warning(f"STUB: Cannot extract text from PowerPoint {file_path} - python-pptx not available")
        return "STUB CONTENT: PowerPoint processing not available in this environment."
EOF

        # Patch extraction_service.py to use the stub
        if [ -f "app/services/extraction_service.py" ]; then
            echo -e "${YELLOW}Patching extraction_service.py to use stub implementation...${NC}"
            cp app/services/extraction_service.py app/services/extraction_service.py.bak

            # Modify the import
            sed -i.bak 's/from pptx import Presentation/# Using stub implementation\ntry:\n    from pptx import Presentation\nexcept ImportError:\n    from app.services.stubs.pptx_stub import Presentation/g' app/services/extraction_service.py
            echo -e "${GREEN}Patched extraction_service.py${NC}"
        fi
    fi

    # Handle missing OAuth credentials
    echo -e "${BLUE}Checking for OAuth credentials...${NC}"
    if [ -z "$GOOGLE_CLIENT_ID" ] || [ -z "$GOOGLE_CLIENT_SECRET" ]; then
        echo -e "${YELLOW}Google OAuth credentials not found. Creating stub implementation...${NC}"

        # Create a task_service_stub.py file if it doesn't exist
        if [ ! -f "app/services/task_service_stub.py" ]; then
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
        else
            echo -e "${GREEN}Task service stub already exists. Skipping creation.${NC}"
        fi

        # Update imports in files that use TaskService if not already patched
        if [ -f "app/api/endpoints/batch.py" ] && ! grep -q "task_service_stub" app/api/endpoints/batch.py; then
            echo -e "${YELLOW}Patching batch.py to use stub implementation...${NC}"
            cp app/api/endpoints/batch.py app/api/endpoints/batch.py.bak

            # Use sed to replace the import
            sed -i.bak "s/from app.services.task_service import TaskService/# Using stub implementation\nfrom app.services.task_service_stub import TaskService/g" app/api/endpoints/batch.py
            echo -e "${GREEN}Patched batch.py${NC}"
        elif [ -f "app/api/endpoints/batch.py" ]; then
            echo -e "${GREEN}batch.py already patched. Skipping.${NC}"
        fi

        echo -e "${YELLOW}Stub implementation for Cloud Tasks ready. The app will log tasks instead of creating them.${NC}"
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
fi

# Create upload directories if they don't exist
echo -e "${BLUE}Creating upload directories...${NC}"
mkdir -p uploads/temp uploads/bucket || handle_error "Failed to create upload directories"
mkdir -p /tmp/processing /tmp/uploads || handle_error "Failed to create temp directories"

# Final setup message
echo -e "${GREEN}Setup complete with quick-start options!${NC}"
echo -e "${YELLOW}The script now defaults to keep the virtual environment and skip dependency installation for speed.${NC}"
echo -e "${BLUE}Run options for future runs:${NC}"
echo -e "  ${GREEN}--recreate-venv${NC} : Create a new virtual environment"
echo -e "  ${GREEN}--install-deps${NC} : Install all dependencies"
echo -e "  ${GREEN}--full-setup${NC} : Perform full setup (recreate venv + install deps)"
echo -e "  ${GREEN}--no-debug${NC} : Disable debug logging for the API"
echo -e "${BLUE}To run the application:${NC}"
echo -e "  ${GREEN}python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload${NC}"

if [ "$QUICK_START" = true ]; then
    echo -e "${BLUE}Starting the server automatically in 3 seconds...${NC}"
    sleep 3
    echo -e "${BLUE}Starting uvicorn server...${NC}"
    python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
else
    echo -e "${BLUE}Press Enter to start the server or Ctrl+C to exit...${NC}"
    read -p ""
    echo -e "${BLUE}Starting uvicorn server...${NC}"
    python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
fi
