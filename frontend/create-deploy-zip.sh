#!/bin/bash

# Create a temporary directory for the files
mkdir -p temp_deploy

# Copy all necessary source files (excluding node_modules, dist, and .angular)
rsync -av --progress ./ temp_deploy/ \
  --exclude node_modules \
  --exclude dist \
  --exclude .angular \
  --exclude .git

# Make the cloud shell setup script executable
chmod +x temp_deploy/cloud-shell-setup.sh

# Create the zip file
zip -r frontend-deploy.zip temp_deploy

# Remove the temporary directory
rm -rf temp_deploy

echo "Created frontend-deploy.zip - ready for cloud shell deployment"
echo "After unzipping in cloud shell, run:"
echo "  cd temp_deploy"
echo "  ./cloud-shell-setup.sh" 