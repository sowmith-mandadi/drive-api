#!/bin/bash
# Setup script for Google Cloud Shell environment

# Exit on error
set -e

echo "Setting up Drive API project in Google Cloud Shell..."

# Create Python virtual environment
echo "Creating Python virtual environment..."
python -m venv venv
source venv/bin/activate

# Install backend dependencies
echo "Installing backend dependencies..."
pip install -r backend/requirements.txt

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Configure GCP project
echo "Configuring Google Cloud project..."
if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
  echo "GOOGLE_CLOUD_PROJECT environment variable is not set."
  echo "Please run: gcloud config set project YOUR_PROJECT_ID"
  exit 1
fi

# Create .env file from example if it doesn't exist
if [ ! -f "backend/.env" ]; then
  echo "Creating .env file from example..."
  cp backend/.env.example backend/.env
  # Replace placeholders with actual project ID
  sed -i "s/your-project-id/$GOOGLE_CLOUD_PROJECT/g" backend/.env
  echo "Please edit backend/.env to complete your configuration"
fi

echo "Setup complete!"
echo ""
echo "To run the backend:"
echo "  cd backend"
echo "  source ../venv/bin/activate"
echo "  python run.py"
echo ""
echo "To run the frontend:"
echo "  cd frontend"
echo "  npm start" 