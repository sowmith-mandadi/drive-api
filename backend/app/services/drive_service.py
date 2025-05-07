"""
Google Drive integration service for the FastAPI application.
"""
import logging
import os
import time
import random
import re
from typing import Any, Dict, List, Optional, Tuple, BinaryIO

from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
import google.auth.transport.requests

from app.core.config import settings

# Setup logging
logger = logging.getLogger(__name__)


class DriveService:
    """Service for Google Drive API integration."""

    def __init__(self, credentials: Optional[Dict[str, Any]] = None):
        """Initialize the Drive service with OAuth credentials or service account.

        Args:
            credentials: OAuth credentials dictionary with token, refresh_token, etc.
                        If None, will try to use service account.
        """
        try:
            # First check if service account path is specified
            service_account_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_PATH")
            
            if service_account_path and os.path.exists(service_account_path):
                # Use service account if available
                try:
                    logger.info(f"Initializing Drive service with service account from {service_account_path}")
                    self.creds = service_account.Credentials.from_service_account_file(
                        service_account_path,
                        scopes=["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file", 
                                "https://www.googleapis.com/auth/drive.readonly"]
                    )
                    self.service = build("drive", "v3", credentials=self.creds)
                    self.service_account_path = service_account_path
                    self.has_service_account = True
                    logger.info(f"Successfully initialized Drive service with service account: {self.creds.service_account_email}")
                except Exception as e:
                    logger.error(f"Failed to initialize with service account: {str(e)}")
                    self.has_service_account = False
                    raise RuntimeError(f"Service account initialization failed: {str(e)}")
            elif credentials:
                # Use OAuth credentials if provided
                logger.info("Initializing Drive service with OAuth credentials")
                self.creds = Credentials(
                    token=credentials.get("token"),
                    refresh_token=credentials.get("refresh_token"),
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=settings.GOOGLE_CLIENT_ID,
                    client_secret=settings.GOOGLE_CLIENT_SECRET,
                    scopes=settings.GOOGLE_DRIVE_SCOPES,
                )
                self.service = build("drive", "v3", credentials=self.creds)
                self.has_service_account = False
                logger.info("Successfully initialized Drive service with OAuth credentials")
            else:
                # Last resort: Try to use application default credentials
                logger.info("No explicit credentials provided, attempting to use application default credentials")
                from google.auth import default
                creds, project = default()
                self.service = build("drive", "v3", credentials=creds)
                self.has_service_account = False
                logger.info(f"Drive service initialized with application default credentials, project: {project}")
        except Exception as e:
            logger.error(f"Failed to initialize Drive service: {str(e)}")
            raise RuntimeError(f"Drive service initialization failed: {str(e)}")

    def list_files(self, page_size: int = 100) -> List[Dict[str, Any]]:
        """List files from Google Drive.

        Args:
            page_size: Number of files to return.

        Returns:
            List of file metadata.
        """
        try:
            results = (
                self.service.files()
                .list(
                    pageSize=page_size,
                    fields="files(id, name, mimeType, webViewLink, thumbnailLink, iconLink, size)",
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True,
                )
                .execute()
            )

            files = results.get("files", [])
            logger.info(f"Retrieved {len(files)} files from Drive")
            return files
        except HttpError as error:
            logger.error(f"Error listing files: {str(error)}")
            raise

    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """Get metadata for a specific file.

        Args:
            file_id: ID of the file in Google Drive.

        Returns:
            File metadata.
        """
        try:
            file = (
                self.service.files()
                .get(
                    fileId=file_id,
                    fields="id, name, mimeType, webViewLink, thumbnailLink, iconLink, size",
                    supportsAllDrives=True,
                )
                .execute()
            )

            logger.info(f"Retrieved metadata for file {file_id}")
            return file
        except HttpError as error:
            logger.error(f"Error getting file metadata: {str(error)}")
            raise

    def get_files_metadata(self, file_ids: List[str]) -> List[Dict[str, Any]]:
        """Get metadata for multiple files.

        Args:
            file_ids: List of file IDs.

        Returns:
            List of file metadata.
        """
        files = []
        for file_id in file_ids:
            try:
                file = self.get_file_metadata(file_id)
                files.append(file)
            except Exception as e:
                logger.error(f"Error getting metadata for file {file_id}: {str(e)}")
                # Continue with other files even if one fails
                continue

        logger.info(f"Retrieved metadata for {len(files)} out of {len(file_ids)} files")
        return files

    def download_file(self, file_id: str, destination_path: str) -> bool:
        """Download a file from Google Drive.

        Args:
            file_id: ID of the file in Google Drive.
            destination_path: Path to save the file.

        Returns:
            True if successful, False otherwise.
        """
        try:
            request = self.service.files().get_media(fileId=file_id, supportsAllDrives=True)

            with open(destination_path, "wb") as f:
                downloader = request.execute()
                f.write(downloader)

            logger.info(f"File {file_id} downloaded to {destination_path}")
            return True
        except HttpError as error:
            logger.error(f"Error downloading file: {str(error)}")
            return False
            
    def download_large_file(self, file_id: str, destination_path: str, mime_type: Optional[str] = None) -> bool:
        """Download a large file, including Google Workspace files that require export, with specialized handling
        for files that might trigger 'exportSizeLimitExceeded' errors.

        Args:
            file_id: ID of the file in Google Drive
            destination_path: Path to save the file 
            mime_type: Optional MIME type to export Google Workspace files to

        Returns:
            True if successful, False otherwise
        """
        try:
            # First get file metadata to determine file type
            file_metadata = self.service.files().get(
                fileId=file_id,
                fields="id,name,mimeType,size",
                supportsAllDrives=True
            ).execute()
            
            file_mime = file_metadata.get('mimeType', '')
            file_name = file_metadata.get('name', 'unknown')
            logger.info(f"Downloading large file: {file_name} ({file_mime})")
            
            # Check if it's a Google Workspace file that needs exporting
            if file_mime.startswith('application/vnd.google-apps.'):
                if not mime_type:
                    # Set default export type based on Google file type
                    if file_mime == 'application/vnd.google-apps.document':
                        mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'  # docx
                    elif file_mime == 'application/vnd.google-apps.spreadsheet':
                        mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'  # xlsx
                    elif file_mime == 'application/vnd.google-apps.presentation':
                        mime_type = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'  # pptx
                    else:
                        mime_type = 'application/pdf'  # default to PDF for other types
                
                # Try regular export first
                try:
                    logger.info(f"Attempting to export {file_name} as {mime_type}")
                    request = self.service.files().export_media(
                        fileId=file_id,
                        mimeType=mime_type
                    )
                    
                    with open(destination_path, 'wb') as f:
                        downloader = MediaIoBaseDownload(f, request)
                        done = False
                        while done is False:
                            status, done = downloader.next_chunk()
                            logger.info(f"Export download {int(status.progress() * 100)}%.")
                    
                    # Verify file was downloaded
                    if os.path.exists(destination_path) and os.path.getsize(destination_path) > 0:
                        logger.info(f"Successfully exported file to {destination_path}")
                        return True
                    else:
                        logger.warning(f"Export succeeded but file is empty")
                        # Fall through to direct export URL method
                except HttpError as e:
                    error_content = str(e)
                    if "exportSizeLimitExceeded" in error_content:
                        logger.warning(f"File too large for API export: {error_content}")
                        # Fall through to direct export URL method
                    else:
                        logger.error(f"Error exporting file: {error_content}")
                        return False
                
                # For large files that exceeded the export size limit,
                # try direct export URL with authentication
                try:
                    logger.info(f"Attempting direct export URL download for large file: {file_name}")
                    
                    # Determine the direct export URL based on file type
                    if file_mime == 'application/vnd.google-apps.presentation':
                        export_url = f"https://docs.google.com/presentation/d/{file_id}/export/pptx"
                        export_format = "pptx"
                    elif file_mime == 'application/vnd.google-apps.document':
                        export_url = f"https://docs.google.com/document/d/{file_id}/export/docx"
                        export_format = "docx"
                    elif file_mime == 'application/vnd.google-apps.spreadsheet':
                        export_url = f"https://docs.google.com/spreadsheets/d/{file_id}/export/xlsx"
                        export_format = "xlsx"
                    else:
                        export_url = f"https://docs.google.com/document/d/{file_id}/export/pdf"
                        export_format = "pdf"
                    
                    logger.info(f"Using direct export URL: {export_url}")
                    
                    # Get an auth token for the URL
                    success, response = self._download_with_direct_export_url(export_url, destination_path)
                    if success:
                        return True
                    else:
                        logger.error("Direct export URL download failed")
                        return False
                except Exception as ex:
                    logger.error(f"Error with direct export URL: {str(ex)}")
                    return False
            else:
                # Regular file download
                try:
                    request = self.service.files().get_media(fileId=file_id, supportsAllDrives=True)
                    
                    with open(destination_path, 'wb') as f:
                        downloader = MediaIoBaseDownload(f, request)
                        done = False
                        while done is False:
                            status, done = downloader.next_chunk()
                            logger.info(f"Download {int(status.progress() * 100)}%.")
                    
                    # Verify file was downloaded
                    if os.path.exists(destination_path) and os.path.getsize(destination_path) > 0:
                        logger.info(f"Successfully downloaded file to {destination_path}")
                        return True
                    else:
                        logger.warning(f"Download succeeded but file is empty")
                        return False
                except Exception as e:
                    logger.error(f"Error downloading file: {str(e)}")
                    return False
                
        except Exception as e:
            logger.error(f"Error in download_large_file: {str(e)}")
            return False
            
    def _download_with_direct_export_url(self, export_url: str, destination_path: str, max_retries: int = 3) -> Tuple[bool, Optional[Dict]]:
        """
        Download a file using direct export URL with service account authentication.
        
        Args:
            export_url: Direct export URL 
            destination_path: Path to save the file
            max_retries: Maximum number of retry attempts
            
        Returns:
            Tuple of (success boolean, response data or None)
        """
        import requests
        
        # Check if service account is available
        if not self.has_service_account:
            logger.error("No service account available for authenticated URL download")
            return False, None
            
        # Extract file ID from URL
        file_id = None
        if "/presentation/d/" in export_url:
            match = re.search(r"/presentation/d/([^/]+)", export_url)
            if match:
                file_id = match.group(1)
        elif "/document/d/" in export_url:
            match = re.search(r"/document/d/([^/]+)", export_url)
            if match:
                file_id = match.group(1)
        elif "/spreadsheets/d/" in export_url:
            match = re.search(r"/spreadsheets/d/([^/]+)", export_url)
            if match:
                file_id = match.group(1)
                
        if not file_id:
            logger.error(f"Could not extract file ID from URL: {export_url}")
            return False, None
            
        # Load fresh credentials for each attempt to avoid token expiration issues
        for attempt in range(max_retries):
            try:
                logger.info(f"Direct export URL download attempt {attempt+1} for {export_url}")
                
                # Create fresh credentials for this attempt
                creds = service_account.Credentials.from_service_account_file(
                    self.service_account_path,
                    scopes=["https://www.googleapis.com/auth/drive.readonly"]
                )
                
                # Get an access token
                auth_token = creds.token
                if not auth_token:
                    # For some credentials we might need to explicitly request a token
                    auth_request = google.auth.transport.requests.Request()
                    creds.refresh(auth_request)
                    auth_token = creds.token
                
                if not auth_token:
                    logger.error("Failed to obtain auth token")
                    time.sleep((2 ** attempt) + (random.random() * 2))
                    continue
                
                # Set up headers with the token
                headers = {
                    'Authorization': f'Bearer {auth_token}',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                # Use stream=True to handle large files
                response = requests.get(export_url, headers=headers, stream=True, timeout=60)
                
                if response.status_code == 200:
                    # Download the file in chunks
                    with open(destination_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    # Verify file was downloaded
                    if os.path.exists(destination_path) and os.path.getsize(destination_path) > 0:
                        file_size = os.path.getsize(destination_path)
                        logger.info(f"Successfully downloaded file with auth token, size: {file_size} bytes")
                        return True, {"file_size": file_size}
                    else:
                        logger.warning("Download succeeded but file is empty")
                elif response.status_code == 401:
                    logger.warning(f"Authentication error (401): Token may have expired")
                else:
                    logger.warning(f"Direct export download failed with status code: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Direct export download attempt {attempt+1} failed: {str(e)}")
                
            # Retry with backoff if more attempts remain
            if attempt < max_retries - 1:
                sleep_time = (2 ** attempt) + (random.random() * 2)
                logger.info(f"Retrying direct export in {sleep_time:.1f} seconds...")
                time.sleep(sleep_time)
        
        logger.error(f"All direct export download attempts failed")
        return False, None
            
    def list_files_in_folder(self, folder_id: str, page_size: int = 100) -> List[Dict[str, Any]]:
        """List files in a specific folder.
        
        Args:
            folder_id: ID of the folder in Google Drive.
            page_size: Number of files to return.
            
        Returns:
            List of file metadata.
        """
        try:
            results = (
                self.service.files()
                .list(
                    q=f"'{folder_id}' in parents",
                    pageSize=page_size,
                    fields="files(id, name, mimeType, webViewLink, thumbnailLink, iconLink, size)",
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True,
                )
                .execute()
            )
            
            files = results.get("files", [])
            logger.info(f"Retrieved {len(files)} files from folder {folder_id}")
            return files
        except HttpError as error:
            logger.error(f"Error listing files in folder {folder_id}: {str(error)}")
            raise
    
    def get_drive_id_for_file(self, file_id: str) -> Optional[str]:
        """Get the drive ID for a specific file.
        
        Args:
            file_id: ID of the file in Google Drive.
            
        Returns:
            Drive ID if the file is in a shared drive, None otherwise.
        """
        try:
            file = (
                self.service.files()
                .get(
                    fileId=file_id,
                    fields="driveId",
                    supportsAllDrives=True,
                )
                .execute()
            )
            
            drive_id = file.get("driveId")
            if drive_id:
                logger.info(f"File {file_id} is in shared drive {drive_id}")
            return drive_id
        except HttpError as error:
            logger.error(f"Error getting drive ID for file {file_id}: {str(error)}")
            return None


def build_drive_service(credentials: Optional[Dict[str, Any]] = None) -> DriveService:
    """
    Build and return a DriveService instance with the provided credentials or service account.

    Args:
        credentials: OAuth credentials dictionary with token, refresh_token, etc.
                    If None, will try to use service account.

    Returns:
        DriveService: An initialized Drive service
    """
    logger.info("Building Drive service")
    return DriveService(credentials)
