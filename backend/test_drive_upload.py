#!/usr/bin/env python3
"""
Script to test uploading content from Google Drive using the service account.

Usage:
  python test_drive_upload.py <drive_file_id> [--service-account-path credentials.json]

This script will:
1. Connect to Google Drive using the service account
2. Download the specified file
3. Create content metadata in Firestore
4. Upload the file to the storage bucket
"""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account

# Import from app
from app.db.firestore_client import FirestoreClient
from app.services.drive_service import DriveService
from app.services.task_service import TaskService


def process_drive_file(drive_file_id: str, title: Optional[str] = None,
                      description: Optional[str] = None) -> bool:
    """
    Process a file from Google Drive directly using the service account.
    
    Args:
        drive_file_id: The Google Drive file ID to process
        title: Optional title for the content
        description: Optional description for the content
        
    Returns:
        True if successful, False otherwise
    """
    print(f"=== Processing Google Drive file: {drive_file_id} ===\n")
    
    # 1. Check if service account credentials file exists
    service_account_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_PATH", "")
    if not service_account_path:
        print("❌ Error: GOOGLE_SERVICE_ACCOUNT_PATH environment variable not set.")
        print("   Set this environment variable to the path of your service account key file.")
        return False
        
    if not os.path.exists(service_account_path):
        print(f"❌ Error: Service account key file not found at '{service_account_path}'")
        return False
        
    print(f"✅ Service account key file found at '{service_account_path}'")
    
    # 2. Initialize the Drive API with service account credentials
    try:
        credentials = service_account.Credentials.from_service_account_file(
            service_account_path,
            scopes=["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.readonly"]
        )
        drive_service = build("drive", "v3", credentials=credentials)
        print(f"✅ Successfully created Drive service with service account credentials")
        
        # Display service account email
        service_email = credentials.service_account_email
        print(f"✅ Using service account: {service_email}")
        
    except Exception as e:
        print(f"❌ Error initializing Drive API: {str(e)}")
        return False
    
    # 3. Get file metadata
    try:
        file = drive_service.files().get(
            fileId=drive_file_id,
            supportsAllDrives=True,
            fields="id,name,mimeType,size,webViewLink,thumbnailLink,driveId,createdTime,modifiedTime"
        ).execute()
        
        file_name = file.get('name', 'Unknown File')
        mime_type = file.get('mimeType', 'application/octet-stream')
        drive_id = file.get('driveId')
        web_view_link = file.get('webViewLink', '')
        thumbnail_link = file.get('thumbnailLink', '')
        file_size = file.get('size')
        created_time = file.get('createdTime')
        modified_time = file.get('modifiedTime')
        
        print(f"✅ Successfully accessed file: {file_name} (ID: {drive_file_id})")
        print(f"   MIME type: {mime_type}")
        
        if drive_id:
            print(f"   ✅ File is in shared drive with ID: {drive_id}")
            
            # Get drive info
            try:
                drive = drive_service.drives().get(driveId=drive_id).execute()
                print(f"   ✅ Shared drive name: {drive.get('name')}")
            except Exception as e:
                print(f"   ⚠️ Could not get shared drive info: {str(e)}")
        else:
            print("   ⚠️ File is not in a shared drive")
            
    except HttpError as error:
        print(f"❌ Error accessing file: {error}")
        return False
    
    # 4. Initialize Firestore for content metadata
    try:
        firestore = FirestoreClient()
        print("✅ Successfully connected to Firestore")
    except Exception as e:
        print(f"❌ Error connecting to Firestore: {str(e)}")
        return False
    
    # 5. Create temporary directory for download
    temp_dir = os.environ.get("TEMP_UPLOAD_DIR", "/tmp/uploads")
    os.makedirs(temp_dir, exist_ok=True)
    
    # 6. Download the file from Drive
    temp_file_path = None
    try:
        # Handle Google Workspace files (Docs, Sheets, Slides)
        if mime_type.startswith('application/vnd.google-apps.'):
            print(f"   ℹ️ This is a Google Workspace file, exporting to appropriate format")
            
            if 'document' in mime_type:
                request = drive_service.files().export_media(
                    fileId=drive_file_id, mimeType='application/pdf'
                )
                exported_format = '.pdf'
                export_mime_type = 'application/pdf'
            elif 'spreadsheet' in mime_type:
                request = drive_service.files().export_media(
                    fileId=drive_file_id, mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                exported_format = '.xlsx'
                export_mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            elif 'presentation' in mime_type:
                request = drive_service.files().export_media(
                    fileId=drive_file_id, mimeType='application/vnd.openxmlformats-officedocument.presentationml.presentation'
                )
                exported_format = '.pptx'
                export_mime_type = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            else:
                request = drive_service.files().export_media(
                    fileId=drive_file_id, mimeType='application/pdf'
                )
                exported_format = '.pdf'
                export_mime_type = 'application/pdf'
                
            # Update mime type for downstream processing
            mime_type = export_mime_type
            temp_file_name = f"{uuid.uuid4()}{exported_format}"
        else:
            # Regular file, just download it
            request = drive_service.files().get_media(
                fileId=drive_file_id, supportsAllDrives=True
            )
            file_extension = os.path.splitext(file_name)[1]
            temp_file_name = f"{uuid.uuid4()}{file_extension}"
        
        # Save the file temporarily
        temp_file_path = os.path.join(temp_dir, temp_file_name)
        with open(temp_file_path, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"   📥 Download progress: {int(status.progress() * 100)}%")
        
        print(f"✅ File downloaded to temporary location: {temp_file_path}")
        
    except Exception as e:
        print(f"❌ Error downloading file: {str(e)}")
        return False
    
    # 7. Create content metadata in Firestore
    try:
        # Generate ID
        content_id = firestore.generate_id()
        
        # Use provided title or file name
        content_title = title if title else file_name
        
        # Create content data
        now = datetime.now()
        
        # Determine session type by mimetype
        session_type = "Presentation"
        if mime_type and "spreadsheet" in mime_type:
            session_type = "Spreadsheet"
        elif mime_type and "document" in mime_type:
            session_type = "Document"
        
        # Create structured content document that aligns with upload.py
        content_data = {
            "id": content_id,
            "title": content_title,
            "description": description or f"This file was imported directly from Google Drive using service account",
            "abstract": None,
            "session_id": None,
            "status": "processing",
            "source": "drive",
            "track": "Imported",  # Default track
            "sessionType": session_type,
            "tags": ["drive", "imported"],
            "demoType": None,
            "sessionDate": None,
            "durationMinutes": None,
            "learningLevel": None,
            "topics": [],
            "targetJobRoles": [],
            "areasOfInterest": [],
            "industry": None,
            "presenters": [],
            "dateCreated": now.isoformat(),
            "dateModified": now.isoformat(),
            "fileUrls": [],
            "driveUrls": [{
                "driveId": drive_file_id,
                "webViewLink": web_view_link,
                "thumbnailLink": thumbnail_link,
                "name": file_name,
                "mimeType": mime_type,
                "size": file_size,
                "createdTime": created_time,
                "modifiedTime": modified_time,
                "source": "drive"
            }],
            "used": False,
            "aiTags": None,
            "presentationSlidesUrl": None,
            "recapSlidesUrl": None,
            "videoRecordingStatus": None,
            "videoYoutubeUrl": None
        }
        
        # Store in Firestore
        success = firestore.create_document("content", content_id, content_data)
        if not success:
            print(f"❌ Error storing content metadata in Firestore")
            return False
            
        print(f"✅ Content metadata stored in Firestore with ID: {content_id}")
        
        # 8. Process the file with TaskService
        task_service = TaskService()
        task_data = {
            "content_id": content_id,
            "file_path": temp_file_path,
            "file_name": file_name,
            "content_type": mime_type,
            "source": "drive",
            "drive_id": drive_file_id,
        }
        
        # Process file (uploads to storage bucket)
        import asyncio
        process_result = asyncio.run(task_service.process_file(task_data))
        
        if process_result:
            print(f"✅ File successfully processed and uploaded to storage")
            
            # Get the updated content to show URLs
            content = firestore.get_document("content", content_id)
            if content and "fileUrls" in content and content["fileUrls"]:
                print("\nFile URLs:")
                for file_url in content["fileUrls"]:
                    print(f"   🔗 {file_url.get('name')}: {file_url.get('url')}")
                    if file_url.get('gcs_path'):
                        print(f"   🪣 GCS Path: {file_url.get('gcs_path')}")
            
            return True
        else:
            print(f"❌ Error processing file")
            return False
        
    except Exception as e:
        print(f"❌ Error in upload process: {str(e)}")
        # Clean up temp file if it exists
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except:
                pass
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test uploading from Google Drive with service account")
    parser.add_argument("file_id", help="Google Drive file ID to upload")
    parser.add_argument("--service-account-path", help="Path to the service account key file")
    parser.add_argument("--title", help="Title for the content")
    parser.add_argument("--description", help="Description for the content")
    parser.add_argument("--session-type", help="Session type (defaults to one based on file type)")
    parser.add_argument("--track", help="Content track", default="Imported")
    
    args = parser.parse_args()
    
    # Set environment variable if provided
    if args.service_account_path:
        os.environ["GOOGLE_SERVICE_ACCOUNT_PATH"] = args.service_account_path
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = args.service_account_path
    
    # Upload the file from Drive
    success = process_drive_file(args.file_id, args.title, args.description)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1) 