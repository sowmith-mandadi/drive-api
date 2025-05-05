"""
Service for processing content items from bulk uploads.
"""
import os
import re
import uuid
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import requests
from google.cloud import storage
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from app.core.logging import configure_logging
from app.db.firestore_client import FirestoreClient

# Setup logging
logger = configure_logging()


class ContentProcessor:
    """Service for processing content items from bulk uploads."""

    def __init__(self) -> None:
        """Initialize the content processor."""
        try:
            logger.info("Initializing ContentProcessor")

            # Initialize Firestore client
            try:
                self.firestore = FirestoreClient()
                logger.info("ContentProcessor: Firestore client initialized successfully")
            except Exception as db_error:
                logger.error(
                    f"ContentProcessor: Failed to initialize Firestore client: {str(db_error)}",
                    exc_info=True,
                )
                # Re-raise to fail initialization
                raise

            # Use environment variables with proper defaults for App Engine
            # Temporary dir for file processing
            self.temp_dir = os.environ.get("TEMP_PROCESSING_DIR", "/tmp/processing")

            # Initialize Google Cloud Storage
            try:
                self.storage_client = storage.Client()
                bucket_name = os.environ.get("GCS_BUCKET_NAME")
                if not bucket_name:
                    raise ValueError("GCS_BUCKET_NAME environment variable is not set")

                self.bucket = self.storage_client.bucket(bucket_name)
                logger.info(f"ContentProcessor: GCS client initialized with bucket {bucket_name}")

                # Ensure the bucket exists
                if not self.bucket.exists():
                    logger.info(f"Creating Cloud Storage bucket: {bucket_name}")
                    self.storage_client.create_bucket(bucket_name)

            except Exception as gcs_error:
                logger.error(
                    f"ContentProcessor: Failed to initialize GCS client: {str(gcs_error)}",
                    exc_info=True,
                )
                # This is critical - we need storage to function
                raise

            # Check and create temp directory for processing
            try:
                # Create processing directory
                os.makedirs(self.temp_dir, exist_ok=True)
                if not os.path.exists(self.temp_dir):
                    raise Exception(f"Directory {self.temp_dir} could not be created")
                if not os.access(self.temp_dir, os.W_OK):
                    raise Exception(f"Directory {self.temp_dir} is not writable")
                logger.info(f"Using temp directory: {self.temp_dir}")
            except Exception as dir_error:
                logger.error(
                    f"ContentProcessor: Failed to set up temp directory: {str(dir_error)}",
                    exc_info=True,
                )
                # Re-raise to fail initialization
                raise

            logger.info("ContentProcessor initialization completed successfully")

        except Exception as e:
            logger.error(f"Critical error initializing ContentProcessor: {str(e)}", exc_info=True)
            # Re-raise to fail initialization
            raise

    async def process_content_item(
        self,
        content_data: Dict[str, Any],
        file_url: Optional[str] = None,
        drive_file_id: Optional[str] = None,
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Process a content item from bulk upload.

        Args:
            content_data: Content metadata.
            file_url: Optional URL to download file from.
            drive_file_id: Optional direct Google Drive file ID.

        Returns:
            Tuple of (success, message, created_content).
        """
        try:
            # Generate ID
            content_id = self.firestore.generate_id()

            # Set basic fields
            now = datetime.now().isoformat()
            content_data["id"] = content_id
            content_data["created_at"] = now
            content_data["updated_at"] = now
            content_data["fileUrls"] = []

            # Ensure source is set properly
            if drive_file_id or (file_url and self._extract_drive_id(file_url)):
                content_data["source"] = "drive"
            elif file_url and ("youtube.com" in file_url or "youtu.be" in file_url):
                content_data["source"] = "external"
            else:
                content_data["source"] = "upload"

            # Prioritize direct drive file ID if provided
            if drive_file_id and isinstance(drive_file_id, str) and drive_file_id.strip():
                drive_id = drive_file_id.strip()
                success, message, file_info = await self._process_file_from_drive(
                    content_id, drive_id
                )
                if success and file_info:
                    content_data["fileUrls"].append(file_info)
                    content_data["drive_id"] = drive_id
                    if "webViewLink" in file_info:
                        content_data["drive_link"] = file_info["webViewLink"]

            # Process file URL if provided
            elif file_url and isinstance(file_url, str) and file_url.strip():
                # Clean up URL
                file_url = file_url.strip()

                # Check if it's a YouTube URL
                if "youtube.com" in file_url or "youtu.be" in file_url:
                    # Store YouTube link directly, no need to download
                    youtube_id = self._extract_youtube_id(file_url)
                    if youtube_id:
                        # Set YouTube specific fields according to content model
                        content_data["youtube_url"] = file_url
                        content_data["video_youtube_url"] = file_url

                        # Also add to fileUrls for backward compatibility
                        youtube_info = {
                            "url": file_url,
                            "name": f"YouTube Video ({youtube_id})",
                            "type": "video/youtube",
                            "size": 0,
                            "youtubeId": youtube_id,
                            "source": "youtube",
                        }
                        content_data["fileUrls"].append(youtube_info)

                # Check if it's a Drive URL
                else:
                    drive_id = self._extract_drive_id(file_url)

                    if drive_id:
                        # Process file via Drive API
                        success, message, file_info = await self._process_file_from_drive(
                            content_id, drive_id
                        )
                        if success and file_info:
                            content_data["fileUrls"].append(file_info)
                            # Set drive fields according to content model
                            content_data["drive_id"] = drive_id
                            content_data["drive_link"] = file_url

                            # Set proper URL fields based on file type
                            mime_type = file_info.get("type", "")
                            if "presentation" in mime_type:
                                content_data["presentation_slides_url"] = file_info["url"]
                            elif "video" in mime_type:
                                content_data["video_source_file_url"] = file_info["url"]

                    elif file_url.startswith(("http://", "https://", "ftp://")):
                        # Process regular URL
                        success, message, file_info = await self._process_file_from_url(
                            content_id, file_url
                        )
                        if success and file_info:
                            content_data["fileUrls"].append(file_info)
                            content_data["file_path"] = file_info["url"]

            # Ensure tags field exists
            if "tags" not in content_data:
                content_data["tags"] = []

            # Ensure metadata field exists
            if "metadata" not in content_data:
                content_data["metadata"] = {}

            # Set used flag if not present
            if "used" not in content_data:
                content_data["used"] = False

            # Store in Firestore
            success = self.firestore.create_document("content", content_id, content_data)
            if not success:
                return False, "Failed to store content metadata", None

            return True, "Content created successfully", content_data

        except Exception as e:
            logger.error(f"Error processing content item: {str(e)}")
            return False, f"Error processing content: {str(e)}", None

    def _extract_drive_id(self, url_or_id: str) -> Optional[str]:
        """
        Extract Google Drive file ID from URL or return the ID if already an ID.

        Handles various Drive URL formats:
        - https://drive.google.com/file/d/{fileId}/view
        - https://drive.google.com/open?id={fileId}
        - https://docs.google.com/document/d/{fileId}/edit
        - https://docs.google.com/presentation/d/{fileId}/edit
        - etc.

        Returns None if not a Drive URL/ID.
        """
        # If it's a YouTube link, return None to handle it separately
        if "youtube.com" in url_or_id or "youtu.be" in url_or_id:
            return None

        # If it's a short string with no slashes, might be a direct file ID
        if len(url_or_id) >= 25 and len(url_or_id) <= 44 and "/" not in url_or_id:
            return url_or_id

        # Common Drive URL patterns
        file_id_patterns = [
            r"drive\.google\.com/file/d/([^/]+)",
            r"drive\.google\.com/open\?id=([^&]+)",
            r"docs\.google\.com/\w+/d/([^/]+)",
            r"docs\.google\.com/presentation/d/([^/]+)",
            r"drive\.google\.com/drive/folders/([^?&/]+)",
        ]

        for pattern in file_id_patterns:
            match = re.search(pattern, url_or_id)
            if match:
                return match.group(1)

        return None

    def _extract_youtube_id(self, url: str) -> Optional[str]:
        """
        Extract YouTube video ID from various YouTube URL formats.

        Returns None if not a valid YouTube URL.
        """
        youtube_patterns = [
            r"youtube\.com/watch\?v=([^&]+)",
            r"youtu\.be/([^?&/]+)",
            r"youtube\.com/embed/([^?&/]+)",
            r"youtube\.com/v/([^?&/]+)",
        ]

        for pattern in youtube_patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    async def _process_file_from_drive(
        self, content_id: str, file_id: str
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Download and process a file from Google Drive.

        Args:
            content_id: ID of the content.
            file_id: Google Drive file ID.

        Returns:
            Tuple of (success, message, file_info).
        """
        temp_file_path = None

        try:
            # Build the Drive service using App Engine default credentials or service account
            try:
                # Check if a service account file path is specified
                service_account_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_PATH")
                
                if service_account_path and os.path.exists(service_account_path):
                    # Use the service account file if provided
                    from google.oauth2 import service_account
                    credentials = service_account.Credentials.from_service_account_file(
                        service_account_path,
                        scopes=["https://www.googleapis.com/auth/drive.readonly"]
                    )
                    drive_service = build("drive", "v3", credentials=credentials, cache_discovery=False)
                    logger.info("Successfully created Drive service with service account credentials")
                else:
                    # Fall back to default credentials
                    drive_service = build("drive", "v3", cache_discovery=False)
                    logger.info("Successfully created Drive service with default credentials")
            except Exception as auth_error:
                logger.error(f"Failed to authenticate with Google Drive: {str(auth_error)}")
                return False, f"Drive authentication failed: {str(auth_error)}", None

            # Get file metadata with more fields including webViewLink
            try:
                file = (
                    drive_service.files()
                    .get(
                        fileId=file_id,
                        fields="id,name,mimeType,size,webViewLink,thumbnailLink,iconLink",
                        supportsAllDrives=True,
                    )
                    .execute()
                )
            except Exception as meta_error:
                logger.error(f"Failed to get Drive file metadata: {str(meta_error)}")
                return False, f"Failed to access Drive file: {str(meta_error)}", None

            # Check if it's a folder
            if file.get("mimeType") == "application/vnd.google-apps.folder":
                try:
                    # Handle folder by listing files and selecting first file
                    results = (
                        drive_service.files()
                        .list(
                            q=f"'{file_id}' in parents",
                            fields="files(id,name,mimeType,size,webViewLink,thumbnailLink,iconLink)",
                            pageSize=1,  # Just get the first file
                            supportsAllDrives=True,
                            includeItemsFromAllDrives=True,
                        )
                        .execute()
                    )
                    folder_files = results.get("files", [])

                    if not folder_files:
                        return False, "Drive folder is empty", None

                    # Use the first file
                    file_id = folder_files[0]["id"]
                    # Get updated metadata for the specific file
                    file = (
                        drive_service.files()
                        .get(
                            fileId=file_id,
                            fields="id,name,mimeType,size,webViewLink,thumbnailLink,iconLink",
                            supportsAllDrives=True,
                        )
                        .execute()
                    )
                except Exception as folder_error:
                    logger.error(f"Failed to process Drive folder: {str(folder_error)}")
                    return False, f"Failed to process Drive folder: {str(folder_error)}", None

            # Create temp file path
            file_name = file.get("name", f"file_{uuid.uuid4()}")
            temp_file_name = f"{uuid.uuid4()}_{file_name}"
            temp_file_path = os.path.join(self.temp_dir, temp_file_name)

            # Map content types to more standardized types for the content model
            content_type_map = {
                "application/vnd.google-apps.document": "document",
                "application/vnd.google-apps.spreadsheet": "spreadsheet",
                "application/vnd.google-apps.presentation": "presentation",
                "application/pdf": "document",
                "application/vnd.openxmlformats-officedocument.presentationml.presentation": "presentation",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "document",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "spreadsheet",
                "video/mp4": "video",
                "video/quicktime": "video",
                "video/mpeg": "video",
                "video/webm": "video",
                "audio/mpeg": "audio",
                "audio/mp4": "audio",
                "image/jpeg": "image",
                "image/png": "image",
                "image/gif": "image",
            }

            # Handle Google Workspace files (Docs, Sheets, Slides)
            mime_type = file.get("mimeType", "")
            # Get standardized content type or use the original if not mapped
            content_type_category = content_type_map.get(mime_type, "unknown")

            if mime_type.startswith("application/vnd.google-apps."):
                try:
                    if "document" in mime_type:
                        # Export as PDF
                        request = drive_service.files().export_media(
                            fileId=file_id, mimeType="application/pdf", supportsAllDrives=True
                        )
                        file_extension = ".pdf"
                        export_mime_type = "application/pdf"
                    elif "spreadsheet" in mime_type:
                        # Export as Excel
                        request = drive_service.files().export_media(
                            fileId=file_id,
                            mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            supportsAllDrives=True
                        )
                        file_extension = ".xlsx"
                        export_mime_type = (
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    elif "presentation" in mime_type:
                        # Export as PowerPoint
                        request = drive_service.files().export_media(
                            fileId=file_id,
                            mimeType="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                            supportsAllDrives=True
                        )
                        file_extension = ".pptx"
                        export_mime_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
                    else:
                        # Default to PDF for other Google formats
                        request = drive_service.files().export_media(
                            fileId=file_id, mimeType="application/pdf", supportsAllDrives=True
                        )
                        file_extension = ".pdf"
                        export_mime_type = "application/pdf"

                    # Make sure filename has the right extension
                    if not file_name.lower().endswith(file_extension):
                        file_name = f"{os.path.splitext(file_name)[0]}{file_extension}"
                        temp_file_name = f"{uuid.uuid4()}_{file_name}"
                        temp_file_path = os.path.join(self.temp_dir, temp_file_name)

                    # Use the export MIME type
                    mime_type = export_mime_type

                except Exception as export_error:
                    logger.error(f"Failed to export Google Workspace file: {str(export_error)}")
                    return (
                        False,
                        f"Failed to export Google Workspace file: {str(export_error)}",
                        None,
                    )
            else:
                # Regular file
                try:
                    request = drive_service.files().get_media(fileId=file_id, supportsAllDrives=True)
                except Exception as get_error:
                    logger.error(f"Failed to get Drive file: {str(get_error)}")
                    return False, f"Failed to access Drive file: {str(get_error)}", None

            # Download file content
            try:
                with open(temp_file_path, "wb") as f:
                    downloader = MediaIoBaseDownload(f, request)
                    done = False
                    retry_count = 0
                    max_retries = 3

                    while not done and retry_count < max_retries:
                        try:
                            status, done = downloader.next_chunk()
                        except Exception as chunk_error:
                            logger.warning(
                                f"Error downloading chunk, attempt {retry_count+1}: {str(chunk_error)}"
                            )
                            retry_count += 1
                            if retry_count >= max_retries:
                                raise chunk_error
            except Exception as download_error:
                logger.error(f"Failed to download Drive file: {str(download_error)}")
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                return False, f"Failed to download Drive file: {str(download_error)}", None

            # Check file size
            file_size = os.path.getsize(temp_file_path)
            if file_size == 0:
                os.remove(temp_file_path)
                return False, "Downloaded file is empty", None

            # Generate unique storage filename
            file_extension = os.path.splitext(file_name)[1]
            if not file_extension:
                # Try to guess extension from MIME type
                if "pdf" in mime_type.lower():
                    file_extension = ".pdf"
                elif "powerpoint" in mime_type.lower() or "presentation" in mime_type.lower():
                    file_extension = ".pptx"
                elif "word" in mime_type.lower() or "document" in mime_type.lower():
                    file_extension = ".docx"
                elif "excel" in mime_type.lower() or "spreadsheet" in mime_type.lower():
                    file_extension = ".xlsx"
                else:
                    file_extension = ""

            storage_filename = f"{uuid.uuid4()}{file_extension}"

            # Upload to Google Cloud Storage
            try:
                # Create blob path with folder prefix
                folder_prefix = os.environ.get("GCS_FOLDER_PREFIX", "uploads")
                blob_path = f"{folder_prefix}/{storage_filename}"
                blob = self.bucket.blob(blob_path)

                # Upload file with content type
                blob.upload_from_filename(temp_file_path, content_type=mime_type)

                # Generate a public URL for the file
                if os.environ.get("GCS_MAKE_PUBLIC", "").lower() == "true":
                    blob.make_public()
                    public_url = blob.public_url
                else:
                    # Generate a signed URL that expires after a period
                    expiration = int(
                        os.environ.get("GCS_URL_EXPIRATION", "86400")
                    )  # Default 24 hours
                    public_url = blob.generate_signed_url(
                        version="v4", expiration=expiration, method="GET"
                    )

                logger.info(f"File uploaded to GCS: {blob_path}")

                # Delete temp file when done
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                    temp_file_path = None

                # Store GCS path for internal reference
                bucket_name = os.environ.get("GCS_BUCKET_NAME")
                gcs_path = f"gs://{bucket_name}/{blob_path}"

                # Return file info with Drive metadata
                file_info = {
                    "url": public_url,
                    "name": file_name,
                    "type": mime_type,
                    "contentType": content_type_category,
                    "size": file_size,
                    "driveId": file_id,
                    "webViewLink": file.get("webViewLink", ""),
                    "thumbnailLink": file.get("thumbnailLink", ""),
                    "iconLink": file.get("iconLink", ""),
                    "source": "drive",
                    "gcs_path": gcs_path,
                }

                return True, "File processed successfully", file_info

            except Exception as gcs_error:
                logger.error(f"Failed to upload to GCS: {str(gcs_error)}")
                return False, f"Failed to store file in Cloud Storage: {str(gcs_error)}", None

        except Exception as e:
            logger.error(f"Failed to process Drive file {file_id}: {str(e)}")
            # Clean up temp file if it exists
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except Exception:
                    pass
            return False, f"Failed to process Drive file: {str(e)}", None

    async def _process_file_from_url(
        self, content_id: str, file_url: str
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Download and process a file from a URL.

        Args:
            content_id: ID of the content.
            file_url: URL to download file from.

        Returns:
            Tuple of (success, message, file_info).
        """
        temp_file_path = None
        try:
            # Get file name from URL or generate one
            file_name = os.path.basename(file_url.split("?")[0])
            if not file_name:
                file_name = f"file_{uuid.uuid4()}"

            # Create temp file path with unique name to avoid collisions
            temp_file_name = f"{uuid.uuid4()}_{file_name}"
            temp_file_path = os.path.join(self.temp_dir, temp_file_name)

            # Download file with timeout and error handling
            try:
                response = requests.get(file_url, stream=True, timeout=30)
                response.raise_for_status()  # Raise exception for 4XX/5XX responses
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to download file from {file_url}: {str(e)}")
                return False, f"Failed to download file: {str(e)}", None

            with open(temp_file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # Filter out keep-alive chunks
                        f.write(chunk)

            # Check if file was actually downloaded (empty files are suspicious)
            file_size = os.path.getsize(temp_file_path)
            if file_size == 0:
                os.remove(temp_file_path)
                return False, "Downloaded file is empty", None

            # Determine content type (or use a generic one)
            content_type = response.headers.get("Content-Type", "application/octet-stream")

            # Generate a unique file name for storage
            file_extension = os.path.splitext(file_name)[1]
            if not file_extension:
                # Try to guess extension from content type
                if "pdf" in content_type.lower():
                    file_extension = ".pdf"
                elif "powerpoint" in content_type.lower() or "presentation" in content_type.lower():
                    file_extension = ".pptx"
                elif "word" in content_type.lower() or "document" in content_type.lower():
                    file_extension = ".docx"
                elif "excel" in content_type.lower() or "spreadsheet" in content_type.lower():
                    file_extension = ".xlsx"
                else:
                    file_extension = ""

            storage_filename = f"{uuid.uuid4()}{file_extension}"

            # Upload to Google Cloud Storage
            try:
                # Create blob path with folder prefix
                folder_prefix = os.environ.get("GCS_FOLDER_PREFIX", "uploads")
                blob_path = f"{folder_prefix}/{storage_filename}"
                blob = self.bucket.blob(blob_path)

                # Upload file with content type
                blob.upload_from_filename(temp_file_path, content_type=content_type)

                # Generate a public URL for the file
                if os.environ.get("GCS_MAKE_PUBLIC", "").lower() == "true":
                    blob.make_public()
                    public_url = blob.public_url
                else:
                    # Generate a signed URL that expires after a period
                    expiration = int(
                        os.environ.get("GCS_URL_EXPIRATION", "86400")
                    )  # Default 24 hours
                    public_url = blob.generate_signed_url(
                        version="v4", expiration=expiration, method="GET"
                    )

                logger.info(f"File uploaded to GCS: {blob_path}")

                # Delete temp file when done
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                    temp_file_path = None

                # Store GCS path for internal reference
                bucket_name = os.environ.get("GCS_BUCKET_NAME")
                gcs_path = f"gs://{bucket_name}/{blob_path}"

                # Return file info
                file_info = {
                    "url": public_url,
                    "name": file_name,
                    "type": content_type,
                    "size": file_size,
                    "source": "url",
                    "gcs_path": gcs_path,
                }

                return True, "File processed successfully", file_info

            except Exception as gcs_error:
                logger.error(f"Failed to upload to GCS: {str(gcs_error)}")
                return False, f"Failed to store file in Cloud Storage: {str(gcs_error)}", None

        except Exception as e:
            logger.error(f"Error processing file from URL: {str(e)}")
            # Clean up any temp file
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            return False, f"Error processing file: {str(e)}", None
