#!/bin/bash

# This script helps set up the Angular frontend in a cloud shell environment

# Check Node.js version
echo "Checking Node.js version..."
NODE_VERSION=$(node -v)
echo "Current Node.js version: $NODE_VERSION"

# Install dependencies
echo "Installing dependencies..."
npm install

# Configure for cloud environment
echo "Configuring for cloud environment..."
# Update proxy configuration if needed
# Uncomment and modify the following line to update the backend API URL:
# sed -i 's|http://localhost:8000|https://your-backend-url|g' proxy.conf.json

# Build the application
echo "Building the application..."
npm run build

echo "Setup complete! Run 'npm start' to start the development server."
echo "For production, the build output is in the 'dist' directory." 