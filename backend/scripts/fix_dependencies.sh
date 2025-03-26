#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing packages one by one with compatible versions..."

# Core packages
pip install flask==2.3.3
pip install flask-cors==4.0.0
pip install python-dotenv==1.0.0
pip install gunicorn==21.2.0

# Firebase/Google Cloud dependencies
pip install firebase-admin==6.4.0
pip install google-cloud-firestore>=2.20.1
pip install google-cloud-storage>=2.19.0
pip install google-cloud-aiplatform>=1.85.0
pip install vertexai==0.0.1

# Data processing libraries
pip install numpy>=2.2.4
pip install pypdf==3.17.1

# Install newer, compatible version of Pillow first
pip install Pillow>=11.0.0

# Install python-pptx after Pillow is installed
pip install python-pptx>=1.0.2

echo "Dependencies updated successfully!"
echo "Testing if the app can run now..."
echo "You can press Ctrl+C to stop the app after it starts"
sleep 2

# Try to run the app on port 3001
PORT=3001 python run.py 