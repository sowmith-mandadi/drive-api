#!/usr/bin/env python3
"""
Script to generate indexing payloads and send them to the indexer API.

This script first generates payload files for all content in Firestore using
generate_index_payload.py, then sends those payloads to the indexer API
using index_content.py.

Usage:
    python index_all_content.py --endpoint https://indexer-api-url.com/index
"""

import argparse
import logging
import os
import subprocess
import sys
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def run_command(command, description):
    """
    Run a shell command and log output.
    
    Args:
        command: The command to run
        description: Description of what the command does
        
    Returns:
        True if command succeeded, False otherwise
    """
    logger.info(f"Running: {description}")
    logger.info(f"Command: {command}")
    
    try:
        # Run the command and capture output
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Log output
        if result.stdout:
            for line in result.stdout.splitlines():
                logger.info(f"OUT: {line}")
        
        if result.stderr:
            for line in result.stderr.splitlines():
                logger.warning(f"ERR: {line}")
        
        logger.info(f"Command completed successfully with exit code {result.returncode}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with exit code {e.returncode}")
        if e.stdout:
            for line in e.stdout.splitlines():
                logger.info(f"OUT: {line}")
        
        if e.stderr:
            for line in e.stderr.splitlines():
                logger.error(f"ERR: {line}")
        
        return False
        
    except Exception as e:
        logger.error(f"Failed to run command: {e}")
        return False

def main():
    """Main function to run the entire indexing process."""
    parser = argparse.ArgumentParser(description="Generate and send content payloads to indexer API")
    parser.add_argument("--endpoint", required=True, help="Indexer API endpoint URL")
    parser.add_argument("--credentials", help="Path to service account credentials file (for generate_index_payload.py)")
    parser.add_argument("--output-dir", default="./payloads", help="Directory to store payload JSON files")
    parser.add_argument("--collection", default="content", help="Collection name to use (for generate_index_payload.py)")
    parser.add_argument("--timeout", type=int, default=5, help="Timeout in seconds between API calls")
    parser.add_argument("--skip-generation", action="store_true", help="Skip payload generation, only send existing payloads")
    parser.add_argument("--check-only", action="store_true", help="Only check status of existing tasks, don't send new payloads")
    parser.add_argument("--limit", type=int, default=100, help="Maximum number of documents to process (for generate_index_payload.py)")
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    if not os.path.exists(args.output_dir):
        logger.info(f"Creating output directory: {args.output_dir}")
        os.makedirs(args.output_dir)
    
    # Step 1: Generate payload files if not skipping
    if not args.skip_generation and not args.check_only:
        # Build command for generate_index_payload.py
        generate_command = f"python generate_index_payload.py --output-dir {args.output_dir}"
        
        # Add optional arguments if provided
        if args.credentials:
            generate_command += f" --credentials {args.credentials}"
        if args.collection:
            generate_command += f" --collection {args.collection}"
        if args.limit:
            generate_command += f" --limit {args.limit}"
        
        # Run generate_index_payload.py
        if not run_command(generate_command, "Generating index payloads"):
            logger.error("Failed to generate index payloads")
            sys.exit(1)
    
    # Step 2: Send payloads to indexer API
    if not args.check_only:
        # Build command for index_content.py
        index_command = f"python index_content.py --input-dir {args.output_dir} --endpoint {args.endpoint}"
        
        # Add timeout if provided
        if args.timeout:
            index_command += f" --timeout {args.timeout}"
        
        # Run index_content.py
        if not run_command(index_command, "Sending index payloads to API"):
            logger.error("Failed to send index payloads to API")
            sys.exit(1)
    else:
        # Build command for checking task status only
        check_command = f"python index_content.py --endpoint {args.endpoint} --check-only"
        
        # Add timeout if provided
        if args.timeout:
            check_command += f" --timeout {args.timeout}"
        
        # Run index_content.py in check-only mode
        if not run_command(check_command, "Checking task status"):
            logger.error("Failed to check task status")
            sys.exit(1)
    
    logger.info("Completed all operations successfully")


if __name__ == "__main__":
    main() 