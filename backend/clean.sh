#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
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

echo -e "${GREEN}Cleanup complete! Unnecessary files have been removed.${NC}"
echo -e "${BLUE}Note: Use git to add/commit the .gitignore and updates.${NC}"
