#!/usr/bin/env python3
"""
Main test script for the Conference Content Management API.
This script runs all test modules in sequence for comprehensive system testing.
"""

import os
import sys
import logging
import argparse
import importlib.util
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger(__name__)

def import_module(module_path):
    """Import a module from a file path."""
    try:
        module_name = os.path.basename(module_path).replace('.py', '')
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        logger.error(f"Failed to import module {module_path}: {e}")
        return None

def run_test_module(module_name, module_path):
    """Run a test module and return the result."""
    logger.info(f"\n{'='*80}")
    logger.info(f"Running {module_name} tests...")
    logger.info(f"{'='*80}")
    
    module = import_module(module_path)
    if not module:
        return False
    
    try:
        if hasattr(module, 'run_all_tests'):
            result = module.run_all_tests()
            return result
        else:
            logger.error(f"Module {module_name} does not have a run_all_tests function")
            return False
    except Exception as e:
        logger.error(f"Error running tests in {module_name}: {e}")
        return False

def main():
    """Run all test modules."""
    parser = argparse.ArgumentParser(description='Run all tests for the Conference Content Management API')
    parser.add_argument('--api-url', help='Base URL for the API (default: http://localhost:3001/api)')
    parser.add_argument('--skip', help='Comma-separated list of test modules to skip')
    args = parser.parse_args()
    
    # Set API URL environment variable if provided
    if args.api_url:
        os.environ["API_BASE_URL"] = args.api_url
        logger.info(f"Using API URL: {args.api_url}")
    
    # Parse modules to skip
    skip_modules = []
    if args.skip:
        skip_modules = [s.strip() for s in args.skip.split(',')]
        logger.info(f"Skipping modules: {skip_modules}")
    
    # Define test modules to run
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_modules = {
        "drive_api": os.path.join(current_dir, "test_drive_api.py"),
        "services": os.path.join(current_dir, "test_services.py"),
        "vector_search": os.path.join(current_dir, "test_vector_search.py")
    }
    
    # Run each test module
    results = {}
    start_time = datetime.now()
    
    for module_name, module_path in test_modules.items():
        if module_name in skip_modules:
            logger.info(f"Skipping {module_name} tests")
            continue
        
        if not os.path.exists(module_path):
            logger.error(f"Test module not found: {module_path}")
            results[module_name] = False
            continue
        
        results[module_name] = run_test_module(module_name, module_path)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Print summary
    logger.info(f"\n\n{'='*80}")
    logger.info(f"TEST SUMMARY - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"{'='*80}")
    
    all_passed = True
    for module_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{module_name}: {status}")
        all_passed = all_passed and result
    
    logger.info(f"\nTotal test duration: {duration:.2f} seconds")
    logger.info(f"\nOverall result: {'✅ PASSED' if all_passed else '❌ FAILED'}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main()) 