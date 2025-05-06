#!/bin/bash
# Run script for the FastAPI application with proper credentials

# Set Google Cloud credential environment variables
export GOOGLE_APPLICATION_CREDENTIALS="credentials.json"
export GOOGLE_SERVICE_ACCOUNT_PATH="credentials.json"

# Set additional environment variables for debugging
export DEBUG="true"
export USE_GCS="true"

# Run the application in debug mode
echo "Starting application with service account credentials..."
echo "Using credentials file: $GOOGLE_APPLICATION_CREDENTIALS"

python -c "import json; f=open('$GOOGLE_APPLICATION_CREDENTIALS'); data=json.load(f); print(f'Service account email: {data.get(\"client_email\", \"unknown\")}')"

# Attempt to run the test scripts first to verify credential access
echo -e "\nTesting Drive API access..."
python test_service_account.py

echo -e "\nTesting Firestore access..."
python test_firestore.py

# Run the actual application
echo -e "\nStarting FastAPI application..."
python main.py 