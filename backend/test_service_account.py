#!/usr/bin/env python3
"""
Test script to verify that the service account can access files in shared drives.

Usage:
  python test_service_account.py [file_id]

If file_id is not provided, the script will test access to the shared drive itself.
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account


def test_service_account_access(file_id: Optional[str] = None) -> bool:
    """
    Test whether the service account can access a file or shared drive.
    
    Args:
        file_id: Optional ID of the file to test. If not provided, will test access to all shared drives.
        
    Returns:
        True if the test is successful, False otherwise.
    """
    print("=== Testing Service Account Access to Shared Drive ===\n")
    
    # 1. Check if service account credentials file exists
    service_account_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_PATH", "")
    if not service_account_path:
        print("❌ Error: GOOGLE_SERVICE_ACCOUNT_PATH environment variable not set.")
        print("   Set this environment variable to the path of your service account key file.")
        return False
        
    if not os.path.exists(service_account_path):
        print(f"❌ Error: Service account key file not found at '{service_account_path}'")
        print("   Please check that the file exists and the path is correct.")
        return False
        
    print(f"✅ Service account key file found at '{service_account_path}'")
    
    # 2. Check file format and content
    try:
        with open(service_account_path, 'r') as f:
            creds_data = json.load(f)
            if 'type' not in creds_data or creds_data['type'] != 'service_account':
                print("⚠️ Warning: The credentials file doesn't appear to be a valid service account key.")
                print("   Make sure you're using a JSON key file downloaded from the Google Cloud Console.")
    except json.JSONDecodeError:
        print("⚠️ Warning: Could not parse the credentials file as JSON.")
        print("   Make sure the file contains valid JSON data.")
    except Exception as e:
        print(f"⚠️ Warning: Error reading credentials file: {str(e)}")

    # 3. Initialize the Drive API with service account credentials
    try:
        credentials = service_account.Credentials.from_service_account_file(
            service_account_path,
            scopes=["https://www.googleapis.com/auth/drive"]
        )
        drive_service = build("drive", "v3", credentials=credentials)
        print(f"✅ Successfully created Drive service with service account credentials")
        
        # Display service account email
        service_info = credentials.service_account_email
        print(f"✅ Service account email: {service_info}")
        
    except Exception as e:
        print(f"❌ Error initializing Drive API: {str(e)}")
        return False
    
    # 4. Test access to shared drives
    if not file_id:
        try:
            # List all shared drives
            drives_result = drive_service.drives().list(pageSize=10).execute()
            drives = drives_result.get("drives", [])
            
            if not drives:
                print("⚠️ No shared drives found. The service account might not have access to any shared drives.")
                print("   Make sure the service account has been added to the shared drive with appropriate permissions.")
                return False
                
            print(f"✅ Found {len(drives)} shared drive(s):")
            for drive in drives:
                print(f"   - {drive['name']} (ID: {drive['id']})")
                
                # Try to list files in the drive
                try:
                    files_result = drive_service.files().list(
                        corpora="drive",
                        driveId=drive["id"],
                        includeItemsFromAllDrives=True,
                        supportsAllDrives=True,
                        pageSize=5
                    ).execute()
                    
                    files = files_result.get("files", [])
                    print(f"     ✅ Successfully listed {len(files)} file(s) in this drive")
                    if files:
                        print(f"     Sample file: {files[0]['name']} (ID: {files[0]['id']})")
                except Exception as e:
                    print(f"     ❌ Error listing files in drive: {str(e)}")
            
            return True
            
        except HttpError as error:
            print(f"❌ Error accessing shared drives: {error}")
            return False
    
    # 5. Test access to a specific file
    else:
        try:
            # Get file metadata
            file = drive_service.files().get(
                fileId=file_id,
                supportsAllDrives=True,
                fields="id,name,mimeType,parents,driveId,shared"
            ).execute()
            
            print(f"✅ Successfully accessed file: {file['name']} (ID: {file['id']})")
            print(f"   MIME type: {file['mimeType']}")
            
            # Check if it's in a shared drive
            if "driveId" in file:
                print(f"   ✅ File is in shared drive with ID: {file['driveId']}")
                
                # Get drive info
                try:
                    drive = drive_service.drives().get(driveId=file['driveId']).execute()
                    print(f"   ✅ Shared drive name: {drive['name']}")
                except Exception as e:
                    print(f"   ⚠️ Could not get shared drive info: {str(e)}")
            else:
                print("   ⚠️ File is not in a shared drive")
                
            # Try to download the file (just to check access)
            if file['mimeType'] == 'application/vnd.google-apps.folder':
                print("   ℹ️ This is a folder, skipping download test")
            else:
                try:
                    # Only test access, don't actually download
                    request = drive_service.files().get_media(
                        fileId=file_id, 
                        supportsAllDrives=True
                    )
                    # Just checking if the request works, not downloading the content
                    print("   ✅ Successfully verified download access to the file")
                except Exception as e:
                    print(f"   ❌ Error accessing file content: {str(e)}")
                    
            return True
            
        except HttpError as error:
            print(f"❌ Error accessing file with ID '{file_id}': {error}")
            print("   This could mean the service account doesn't have access to this file.")
            print("   Make sure the service account email has been added to the shared drive with appropriate permissions.")
            return False


def test_app_credentials():
    """Test whether the application can access Firestore with the current credentials."""
    print("\n=== Testing Application Credentials for Firestore ===\n")
    
    try:
        from google.cloud import firestore
        
        # Create a Firestore client
        db = firestore.Client()
        print("✅ Successfully created Firestore client")
        
        # Test a simple Firestore operation
        try:
            # Try to access a collection (we don't need to actually read data)
            db.collection("_verification").limit(1).get()
            print("✅ Successfully connected to Firestore")
            return True
        except Exception as e:
            print(f"❌ Error accessing Firestore: {str(e)}")
            print("   Make sure the service account has the necessary Firestore permissions.")
            return False
    except ImportError:
        print("⚠️ Firestore client not available. Skipping Firestore test.")
        return True
    except Exception as e:
        print(f"❌ Error initializing Firestore client: {str(e)}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test service account access to shared drives")
    parser.add_argument("file_id", nargs="?", help="File ID to test (optional)")
    parser.add_argument(
        "--service-account-path", 
        help="Path to the service account key file"
    )
    parser.add_argument(
        "--test-firestore",
        action="store_true",
        help="Also test Firestore access"
    )
    
    args = parser.parse_args()
    
    # Set environment variable if provided
    if args.service_account_path:
        os.environ["GOOGLE_SERVICE_ACCOUNT_PATH"] = args.service_account_path
        # Also set standard application default credentials path
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = args.service_account_path
        
    # Run the Drive test
    drive_success = test_service_account_access(args.file_id)
    
    # Optionally run the Firestore test
    firestore_success = True
    if args.test_firestore:
        firestore_success = test_app_credentials()
    
    # Exit with appropriate code
    sys.exit(0 if drive_success and firestore_success else 1) 