#!/bin/bash
# Run tests for the Conference CMS API

set -e  # Exit on error

# Set up virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Setting up..."
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Create directories for test reports if they don't exist
mkdir -p coverage_reports/html
mkdir -p test_reports

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Running tests for Conference CMS API ===${NC}"

# Run unit tests
echo -e "\n${YELLOW}Running unit tests...${NC}"
python -m pytest tests/ -m "unit" -v

# Run integration tests (skip if CI environment)
if [ "$CI" != "true" ]; then
    echo -e "\n${YELLOW}Running integration tests...${NC}"
    python -m pytest tests/ -m "integration" -v
else
    echo -e "\n${YELLOW}Skipping integration tests in CI environment${NC}"
fi

# Run API contract tests
echo -e "\n${YELLOW}Running API contract tests...${NC}"
python -m pytest tests/test_api_contract.py -v

# Run e2e tests (skip if CI environment)
if [ "$CI" != "true" ]; then
    echo -e "\n${YELLOW}Running end-to-end tests...${NC}"
    python -m pytest tests/ -m "e2e" -v
else
    echo -e "\n${YELLOW}Skipping e2e tests in CI environment${NC}"
fi

# Run performance tests if explicitly requested
if [ "$RUN_PERFORMANCE" = "true" ]; then
    echo -e "\n${YELLOW}Running performance tests...${NC}"
    python -m pytest tests/ -m "performance" -v
else
    echo -e "\n${YELLOW}Skipping performance tests (use RUN_PERFORMANCE=true to run)${NC}"
fi

# Run full test suite with coverage
echo -e "\n${YELLOW}Running full test suite with coverage...${NC}"
python -m pytest tests/ --cov=app --cov-report=term --cov-report=html:coverage_reports/html

echo -e "\n${GREEN}All tests completed!${NC}"
echo -e "${BLUE}View HTML coverage report at:${NC} coverage_reports/html/index.html"

# Check coverage threshold
COVERAGE=$(python -m coverage report | grep TOTAL | awk '{print $4}' | sed 's/%//')
THRESHOLD=75

echo -e "\n${YELLOW}Code coverage: ${COVERAGE}%${NC}"

if (( $(echo "$COVERAGE < $THRESHOLD" | bc -l) )); then
    echo -e "${RED}Coverage is below the threshold of ${THRESHOLD}%${NC}"
    if [ "$CI" = "true" ]; then
        exit 1
    fi
else
    echo -e "${GREEN}Coverage meets or exceeds the threshold of ${THRESHOLD}%${NC}"
fi

# Run flake8 linting
echo -e "\n${YELLOW}Running code linting...${NC}"
flake8 app/ tests/

echo -e "\n${GREEN}Testing and linting complete.${NC}"
