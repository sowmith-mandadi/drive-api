#!/usr/bin/env python3
"""
Test the download_with_service_account function from batch.py directly.

Usage:
  python test_batch_download.py <drive_file_id> [--service-account-path credentials.json]
"""

import os
import sys
import argparse
import tempfile
import uuid

# Import the download function from batch.py
sys.path.append(os.path.abspath("."))
from app.api.endpoints.batch import download_with_service_account

def test_batch_download(drive_file_id, service_account_path=None):
    """Test the download_with_service_account function from batch.py."""
    
    if not service_account_path:
        service_account_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_PATH")
        if not service_account_path:
            print("❌ Error: GOOGLE_SERVICE_ACCOUNT_PATH not set or provided")
            return False
    
    # Set environment variable for the download function
    os.environ["GOOGLE_SERVICE_ACCOUNT_PATH"] = service_account_path
    
    print(f"✅ Using service account file: {service_account_path}")
    
    # Create a URL from the drive file ID
    url = f"https://docs.google.com/presentation/d/{drive_file_id}/export/pptx"
    print(f"Testing URL: {url}")
    
    # Create a temporary file path for the download
    temp_dir = tempfile.gettempdir()
    temp_file = os.path.join(temp_dir, f"batch_test_{uuid.uuid4()}.pptx")
    print(f"Download target: {temp_file}")
    
    # Call the download function
    print("\nTesting download_with_service_account function from batch.py...")
    success = download_with_service_account(url, temp_file, max_retries=3)
    
    if success:
        file_size = os.path.getsize(temp_file)
        print(f"\n✅ SUCCESS: File downloaded to {temp_file}, size: {file_size} bytes")
        
        # Clean up temp file
        os.remove(temp_file)
        print(f"Cleaned up temp file")
    else:
        print(f"\n❌ FAILURE: Download failed")
    
    return success

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test batch download function")
    parser.add_argument("file_id", help="Google Drive file ID to test")
    parser.add_argument("--service-account-path", help="Path to the service account key file")
    
    args = parser.parse_args()
    
    # Run the test
    success = test_batch_download(args.file_id, args.service_account_path)
    sys.exit(0 if success else 1) 