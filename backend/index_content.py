#!/usr/bin/env python3
"""
Script to send indexed payloads to the indexer API and track task IDs.

This script reads JSON payloads from a directory, sends them to the indexer API,
and tracks the task IDs returned by the API for later status checking.

Usage:
    python index_content.py --input-dir ./example_payload.json --endpoint https://indexer-api-url.com/index
"""

import argparse
import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class IndexerClient:
    """Client for interacting with the indexer API."""

    def __init__(self, endpoint_url: str, timeout_seconds: int = 5):
        """
        Initialize the indexer client.
        
        Args:
            endpoint_url: The URL for the indexer API
            timeout_seconds: Timeout in seconds between API calls
        """
        self.endpoint_url = endpoint_url
        self.timeout_seconds = timeout_seconds
        self.task_ids = {}  # Dictionary to store task IDs by session ID
        self.results_file = "indexing_results.json"
        
        # Load any existing results if available
        self.load_results()
        
        logger.info(f"Indexer client initialized with endpoint: {endpoint_url}")
        logger.info(f"Timeout between requests: {timeout_seconds} seconds")

    def load_results(self):
        """Load existing results from the results file if it exists."""
        if os.path.exists(self.results_file):
            try:
                with open(self.results_file, 'r') as f:
                    self.task_ids = json.load(f)
                logger.info(f"Loaded {len(self.task_ids)} existing task IDs from {self.results_file}")
            except Exception as e:
                logger.error(f"Error loading results file: {e}")
                self.task_ids = {}

    def save_results(self):
        """Save the current results to the results file."""
        try:
            with open(self.results_file, 'w') as f:
                json.dump(self.task_ids, f, indent=2)
            logger.info(f"Saved {len(self.task_ids)} task IDs to {self.results_file}")
        except Exception as e:
            logger.error(f"Error saving results to file: {e}")

    def send_payload(self, session_id: str, payload: Dict[str, Any]) -> bool:
        """
        Send a payload to the indexer API.
        
        Args:
            session_id: The session ID for this payload
            payload: The JSON payload to send
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Sending payload for session {session_id} to {self.endpoint_url}")
            logger.info(f"Payload contains {len(payload.get('file_list', []))} files")
            
            headers = {
                "Content-Type": "application/json",
                # Add any authentication headers if needed
                # "Authorization": "Bearer YOUR_API_KEY"
            }
            
            response = requests.post(
                self.endpoint_url,
                headers=headers,
                json=payload
            )
            
            # Check if the request was successful
            if response.status_code in [200, 201, 202]:
                logger.info(f"Successfully sent payload for session {session_id}")
                
                # Try to parse the response as JSON
                try:
                    response_data = response.json()
                    
                    # Store task ID if available
                    task_id = response_data.get("task_id")
                    if task_id:
                        result = {
                            "task_id": task_id,
                            "status": "submitted",
                            "timestamp": datetime.now().isoformat(),
                            "response": response_data
                        }
                        self.task_ids[session_id] = result
                        logger.info(f"Received task ID: {task_id} for session {session_id}")
                    else:
                        logger.warning(f"No task ID found in response for session {session_id}")
                        result = {
                            "status": "completed",
                            "timestamp": datetime.now().isoformat(),
                            "response": response_data
                        }
                        self.task_ids[session_id] = result
                    
                    # Save results after each successful submission
                    self.save_results()
                    return True
                    
                except ValueError:
                    # Response wasn't JSON
                    logger.warning(f"Response wasn't JSON for session {session_id}: {response.text}")
                    self.task_ids[session_id] = {
                        "status": "unknown",
                        "timestamp": datetime.now().isoformat(),
                        "response_text": response.text
                    }
                    self.save_results()
                    return True
            else:
                logger.error(f"Failed to send payload for session {session_id}: {response.status_code}")
                logger.error(f"Response: {response.text}")
                
                # Store error information
                self.task_ids[session_id] = {
                    "status": "error",
                    "error_code": response.status_code,
                    "timestamp": datetime.now().isoformat(),
                    "error_message": response.text
                }
                self.save_results()
                return False
                
        except Exception as e:
            logger.error(f"Error sending payload for session {session_id}: {e}")
            
            # Store error information
            self.task_ids[session_id] = {
                "status": "exception",
                "timestamp": datetime.now().isoformat(),
                "error_message": str(e)
            }
            self.save_results()
            return False

    def check_task_status(self, session_id: str, task_id: str) -> Dict[str, Any]:
        """
        Check the status of a task with the indexer API.
        
        Args:
            session_id: The session ID for this task
            task_id: The task ID to check
            
        Returns:
            Task status information
        """
        try:
            logger.info(f"Checking status for task {task_id} (session {session_id})")
            
            # If your API provides a status endpoint, use it
            status_url = f"{self.endpoint_url}/status/{task_id}"
            
            headers = {
                "Content-Type": "application/json",
                # Add any authentication headers if needed
                # "Authorization": "Bearer YOUR_API_KEY"
            }
            
            response = requests.get(
                status_url,
                headers=headers
            )
            
            # Check if the request was successful
            if response.status_code == 200:
                try:
                    status_data = response.json()
                    
                    # Update task status
                    self.task_ids[session_id]["status"] = status_data.get("status", "unknown")
                    self.task_ids[session_id]["last_checked"] = datetime.now().isoformat()
                    self.task_ids[session_id]["status_response"] = status_data
                    
                    logger.info(f"Task {task_id} status: {status_data.get('status', 'unknown')}")
                    self.save_results()
                    return status_data
                    
                except ValueError:
                    logger.warning(f"Status response wasn't JSON: {response.text}")
                    self.task_ids[session_id]["status"] = "unknown"
                    self.task_ids[session_id]["last_checked"] = datetime.now().isoformat()
                    self.task_ids[session_id]["status_response_text"] = response.text
                    self.save_results()
                    return {"status": "unknown", "message": response.text}
            else:
                logger.error(f"Failed to check status for task {task_id}: {response.status_code}")
                logger.error(f"Response: {response.text}")
                
                self.task_ids[session_id]["status"] = "error"
                self.task_ids[session_id]["last_checked"] = datetime.now().isoformat()
                self.task_ids[session_id]["status_error"] = {
                    "code": response.status_code,
                    "message": response.text
                }
                self.save_results()
                return {"status": "error", "code": response.status_code, "message": response.text}
                
        except Exception as e:
            logger.error(f"Error checking status for task {task_id}: {e}")
            
            self.task_ids[session_id]["status"] = "exception"
            self.task_ids[session_id]["last_checked"] = datetime.now().isoformat()
            self.task_ids[session_id]["status_error"] = str(e)
            self.save_results()
            return {"status": "exception", "message": str(e)}

    def process_payloads(self, input_dir: str):
        """
        Process all payload files in the input directory.
        
        Args:
            input_dir: Directory containing payload JSON files
        """
        # Ensure the directory exists
        if not os.path.exists(input_dir) or not os.path.isdir(input_dir):
            logger.error(f"Input directory {input_dir} does not exist or is not a directory")
            return
        
        # Get all JSON files in the directory
        json_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]
        
        if not json_files:
            logger.warning(f"No JSON files found in {input_dir}")
            return
        
        logger.info(f"Found {len(json_files)} JSON files to process")
        
        # Process each file
        for i, json_file in enumerate(json_files):
            try:
                # Load the payload
                file_path = os.path.join(input_dir, json_file)
                with open(file_path, 'r') as f:
                    payload = json.load(f)
                
                # Extract session ID from the payload or filename
                if 'session_id' in payload:
                    session_id = payload['session_id']
                else:
                    # Use filename without extension as session ID
                    session_id = os.path.splitext(json_file)[0]
                
                # Check if we've already processed this session
                if session_id in self.task_ids and self.task_ids[session_id].get('status') not in ['error', 'exception']:
                    logger.info(f"Skipping already processed session {session_id}")
                    continue
                
                # Send the payload
                success = self.send_payload(session_id, payload)
                
                # Log progress
                logger.info(f"Processed {i+1}/{len(json_files)}: {json_file} - {'Success' if success else 'Failed'}")
                
                # Sleep between requests to avoid overwhelming the API
                if i < len(json_files) - 1:  # Don't sleep after the last file
                    logger.info(f"Sleeping for {self.timeout_seconds} seconds before next request...")
                    time.sleep(self.timeout_seconds)
                
            except Exception as e:
                logger.error(f"Error processing file {json_file}: {e}")
    
    def check_all_tasks(self):
        """Check the status of all tasks that are in 'submitted' state."""
        # Filter tasks in submitted state
        submitted_tasks = {
            session_id: task_info 
            for session_id, task_info in self.task_ids.items() 
            if task_info.get("status") == "submitted" and "task_id" in task_info
        }
        
        if not submitted_tasks:
            logger.info("No submitted tasks to check")
            return
        
        logger.info(f"Checking status for {len(submitted_tasks)} submitted tasks")
        
        # Check each task
        for session_id, task_info in submitted_tasks.items():
            task_id = task_info["task_id"]
            self.check_task_status(session_id, task_id)
            
            # Sleep between requests
            time.sleep(self.timeout_seconds)
        
        logger.info("Finished checking task statuses")


def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description="Send content payloads to indexer API")
    parser.add_argument("--input-dir", default="./example_payload.json", help="Directory containing payload JSON files")
    parser.add_argument("--endpoint", required=True, help="Indexer API endpoint URL")
    parser.add_argument("--timeout", type=int, default=5, help="Timeout in seconds between API calls")
    parser.add_argument("--check-only", action="store_true", help="Only check status of existing tasks, don't send new payloads")
    
    args = parser.parse_args()
    
    # Initialize the client
    client = IndexerClient(args.endpoint, args.timeout)
    
    # Either process new payloads or just check existing tasks
    if args.check_only:
        client.check_all_tasks()
    else:
        # Process payload files
        client.process_payloads(args.input_dir)
        
        # Check task statuses after processing
        client.check_all_tasks()


if __name__ == "__main__":
    main() 