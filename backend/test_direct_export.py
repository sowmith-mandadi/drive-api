#!/usr/bin/env python3
"""
Script to test both download methods for Google Drive files:
1. Using the Drive API with service account (like test_drive_upload.py)
2. Using direct export URLs (like batch.py is trying to do)

Usage:
  python test_direct_export.py <drive_file_id> [--service-account-path credentials.json]
"""

import argparse
import os
import sys
import uuid
import urllib.request
import requests

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account

def test_download_methods(drive_file_id, service_account_path=None):
    """Test different methods for downloading a file from Google Drive."""
    
    if not service_account_path:
        service_account_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_PATH")
        if not service_account_path:
            print("❌ Error: GOOGLE_SERVICE_ACCOUNT_PATH not set or provided")
            return False
    
    if not os.path.exists(service_account_path):
        print(f"❌ Error: Service account file not found at {service_account_path}")
        return False
    
    print(f"✅ Using service account file: {service_account_path}")
    
    # Create a temp directory
    temp_dir = "/tmp/drive_test"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Method 1: Drive API with service account (like in test_drive_upload.py)
    try:
        print("\n=== Testing Method 1: Drive API with service account ===")
        
        # Initialize the drive service with service account
        credentials = service_account.Credentials.from_service_account_file(
            service_account_path,
            scopes=["https://www.googleapis.com/auth/drive.readonly"]
        )
        drive_service = build("drive", "v3", credentials=credentials)
        
        # Get file metadata 
        file = drive_service.files().get(
            fileId=drive_file_id,
            fields="id,name,mimeType",
            supportsAllDrives=True
        ).execute()
        
        file_name = file.get('name', f"file_{uuid.uuid4()}")
        mime_type = file.get('mimeType', 'application/octet-stream')
        
        print(f"✅ Successfully got file metadata: {file_name} ({mime_type})")
        
        # For Google Workspace files (Docs, Sheets, Slides)
        if mime_type.startswith('application/vnd.google-apps.'):
            if "presentation" in mime_type:
                download_mime_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
                file_extension = ".pptx"
            elif "document" in mime_type:
                download_mime_type = "application/pdf"
                file_extension = ".pdf"
            elif "spreadsheet" in mime_type:
                download_mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" 
                file_extension = ".xlsx"
            else:
                download_mime_type = "application/pdf"
                file_extension = ".pdf"
                
            print(f"   Google Workspace file being exported as {download_mime_type}")
            request = drive_service.files().export_media(
                fileId=drive_file_id,
                mimeType=download_mime_type
            )
        else:
            # Regular file - direct download
            print("   Regular file - direct download")
            request = drive_service.files().get_media(
                fileId=drive_file_id,
                supportsAllDrives=True
            )
            file_extension = os.path.splitext(file_name)[1]
            
        # Download the file to a temporary location
        temp_file_path = os.path.join(temp_dir, f"api_download_{uuid.uuid4()}{file_extension}")
        
        with open(temp_file_path, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"   Download progress: {int(status.progress() * 100)}%")
        
        # Check the downloaded file
        file_size = os.path.getsize(temp_file_path)
        print(f"✅ Method 1 SUCCESS: File downloaded to {temp_file_path}, size: {file_size} bytes")
        
    except Exception as e:
        print(f"❌ Method 1 FAILED: {str(e)}")
    
    # Method 2: Direct export URL (like in batch.py)
    try:
        print("\n=== Testing Method 2: Direct export URL ===")
        
        # For Google Slides, construct direct export URL
        direct_export_url = f"https://docs.google.com/presentation/d/{drive_file_id}/export/pptx"
        
        # Also use the same credentials to try authenticated download via requests
        print("Method 2A: Using urllib (no auth)")
        temp_file_path2 = os.path.join(temp_dir, f"direct_export_{uuid.uuid4()}.pptx")
        
        try:
            print(f"   Downloading from: {direct_export_url}")
            urllib.request.urlretrieve(direct_export_url, temp_file_path2)
            
            # Check the downloaded file
            if os.path.exists(temp_file_path2) and os.path.getsize(temp_file_path2) > 0:
                file_size = os.path.getsize(temp_file_path2)
                print(f"✅ Method 2A SUCCESS: File downloaded to {temp_file_path2}, size: {file_size} bytes")
            else:
                print(f"❌ Method 2A FAILED: File is empty or doesn't exist")
        except Exception as e:
            print(f"❌ Method 2A FAILED: {str(e)}")
        
        # Try with requests and auth token from service account
        print("Method 2B: Using requests with auth token")
        temp_file_path3 = os.path.join(temp_dir, f"direct_export_auth_{uuid.uuid4()}.pptx")
        
        try:
            # Get an auth token from the service account
            auth_token = credentials.token
            headers = {'Authorization': f'Bearer {auth_token}'}
            
            print(f"   Downloading from: {direct_export_url} with auth token")
            response = requests.get(direct_export_url, headers=headers, stream=True)
            response.raise_for_status()
            
            with open(temp_file_path3, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Check the downloaded file
            if os.path.exists(temp_file_path3) and os.path.getsize(temp_file_path3) > 0:
                file_size = os.path.getsize(temp_file_path3)
                print(f"✅ Method 2B SUCCESS: File downloaded to {temp_file_path3}, size: {file_size} bytes")
            else:
                print(f"❌ Method 2B FAILED: File is empty or doesn't exist")
        except Exception as e:
            print(f"❌ Method 2B FAILED: {str(e)}")
    
    except Exception as e:
        print(f"❌ Method 2 general error: {str(e)}")
    
    print("\n=== Download Test Summary ===")
    print("Recommendations:")
    print("1. If Method 1 worked but Method 2 failed, update batch.py to use the Drive API with service account")
    print("2. If Method 2B worked but Method 2A failed, add auth headers to your direct URL downloads")
    
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test different download methods for Google Drive")
    parser.add_argument("file_id", help="Google Drive file ID to test")
    parser.add_argument("--service-account-path", help="Path to the service account key file")
    
    args = parser.parse_args()
    
    # Set environment variable if provided
    if args.service_account_path:
        os.environ["GOOGLE_SERVICE_ACCOUNT_PATH"] = args.service_account_path
    
    # Run the test
    test_download_methods(args.file_id, args.service_account_path) 