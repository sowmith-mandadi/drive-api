"""
Google Drive integration service for the FastAPI application.
"""
import logging
import os
from typing import Any, Dict, List, Optional

from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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
                self.creds = service_account.Credentials.from_service_account_file(
                    service_account_path,
                    scopes=settings.GOOGLE_DRIVE_SCOPES
                )
                self.service = build("drive", "v3", credentials=self.creds)
                logger.info(f"Drive service initialized with service account from {service_account_path}")
            elif credentials:
                # Use OAuth credentials if provided
                self.creds = Credentials(
                    token=credentials.get("token"),
                    refresh_token=credentials.get("refresh_token"),
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=settings.GOOGLE_CLIENT_ID,
                    client_secret=settings.GOOGLE_CLIENT_SECRET,
                    scopes=settings.GOOGLE_DRIVE_SCOPES,
                )
                self.service = build("drive", "v3", credentials=self.creds)
                logger.info("Drive service initialized with OAuth credentials")
            else:
                # Try to use default credentials
                self.service = build("drive", "v3", cache_discovery=False)
                logger.info("Drive service initialized with default credentials")
        except Exception as e:
            logger.error(f"Failed to initialize Drive service: {str(e)}")
            raise

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
