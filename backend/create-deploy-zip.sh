#!/bin/bash

# Create a temporary directory for the files
mkdir -p temp_deploy

# Copy all necessary source files (excluding development and cache directories)
rsync -av --progress ./ temp_deploy/ \
  --exclude venv \
  --exclude __pycache__ \
  --exclude .pytest_cache \
  --exclude .mypy_cache \
  --exclude test_reports \
  --exclude coverage_reports \
  --exclude tests \
  --exclude uploads \
  --exclude .git \
  --exclude .vscode \
  --exclude .idea

# Make setup scripts executable
chmod +x temp_deploy/setup.sh
chmod +x temp_deploy/run_cloud_shell.sh

# Create the zip file
zip -r backend-deploy.zip temp_deploy

# Remove the temporary directory
rm -rf temp_deploy

echo "Created backend-deploy.zip - ready for cloud shell deployment"
echo "After unzipping in cloud shell, run:"
echo "  cd temp_deploy"
echo "  ./run_cloud_shell.sh"
