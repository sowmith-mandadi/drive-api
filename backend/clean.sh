#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Cleaning up unnecessary files...${NC}"

# Remove Python cache files
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.so" -delete
find . -name ".DS_Store" -delete

# Remove testing and coverage artifacts (but keep directories)
rm -f .coverage
rm -f coverage.xml
rm -f htmlcov/*
rm -f test_reports/*
rm -f coverage_reports/*

# Keep empty directories with .gitkeep
for dir in uploads coverage_reports test_reports; do
    mkdir -p $dir
    touch $dir/.gitkeep
done

# Clean compiled translations
find . -name "*.mo" -delete

# Delete old zip file if it exists
if [ -f "../backend.zip" ]; then
    echo -e "${YELLOW}Removing old backend.zip file...${NC}"
    rm -f ../backend.zip
fi

echo -e "${GREEN}Cleanup complete! Unnecessary files have been removed.${NC}"

# Create a clean zip file
echo -e "${BLUE}Creating clean zip file of backend code...${NC}"
cd ..
zip -r backend.zip backend/ \
    -x "backend/venv/**" \
    -x "backend/.pytest_cache/**" \
    -x "backend/.mypy_cache/**" \
    -x "backend/__pycache__/**" \
    -x "backend/*/__pycache__/**" \
    -x "backend/*/*/__pycache__/**" \
    -x "backend/*/*/*/__pycache__/**" \
    -x "backend/test_reports/**" \
    -x "backend/coverage_reports/**" \
    -x "backend/.coverage" \
    -x "backend/*.pyc" \
    -x "backend/*.pyo" \
    -x "backend/*.so" \
    -x "backend/**/*.pyc" \
    -x "backend/**/*.pyo" \
    -x "backend/**/*.so"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Successfully created backend.zip with only code-related files!${NC}"
    echo -e "${BLUE}Zip file size: $(du -h backend.zip | cut -f1)${NC}"
else
    echo -e "${RED}Failed to create zip file.${NC}"
fi

echo -e "${BLUE}Note: Use git to add/commit the .gitignore and updates.${NC}"
