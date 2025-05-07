"""
Service for downloading and storing files from Google Drive.
"""
import os
import time
import random
import logging
import tempfile
import urllib.request
import uuid
import requests
from typing import Tuple, Dict, Any, Optional

logger = logging.getLogger(__name__)

class DriveDownloader:
    """
    Service for handling downloads from Google Drive and storing in cloud storage.
    Consolidates various download methods with appropriate fallbacks.
    """
    
    def __init__(self, storage_bucket=None, firestore_client=None):
        """
        Initialize the downloader with storage dependencies.
        
        Args:
            storage_bucket: GCS bucket for file storage
            firestore_client: Firestore client for database updates
        """
        self.bucket = storage_bucket
        self.firestore = firestore_client
        
    async def download_and_store_presentation(self, entry: Dict[str, Any], content_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Download presentation file from Google Drive and store in bucket.
        
        Args:
            entry: File entry with direct export URL
            content_id: Content ID for the item
        
        Returns:
            Success, updated entry with GCS path
        """
        try:
            logger.info(f"Starting file download process for content_id: {content_id}")
            
            # Get the export URL or driveId
            export_url = entry.get("exportUrl") or entry.get("url")
            drive_id = entry.get("driveId")
            presentation_name = entry.get("name")
            
            if not presentation_name or presentation_name in ["Presentation Slides", "Recap Slides"]:
                presentation_name = None
                
            if not export_url and not drive_id:
                logger.warning(f"No valid export URL or driveId found for content {content_id}")
                return False, entry
            
            # Generate a temp file path
            temp_dir = tempfile.gettempdir()
            file_name = f"presentation_{uuid.uuid4()}.pptx"
            temp_file_path = os.path.join(temp_dir, file_name)
            
            # Attempt download with available methods
            success = False
            success, drive_metadata = self._download_file(drive_id, export_url, temp_file_path)
            
            # Update name if we found a better one from metadata
            if success and drive_metadata and drive_metadata.get("name") and not presentation_name:
                presentation_name = drive_metadata.get("name")
                
            # Verify file was actually downloaded
            if not success or not os.path.exists(temp_file_path) or os.path.getsize(temp_file_path) == 0:
                logger.error("Downloaded file is missing or empty")
                return False, entry
                
            file_size = os.path.getsize(temp_file_path)
            
            # Upload to GCS bucket
            public_url, gcs_path = self._upload_to_storage(temp_file_path, file_name)
            if not public_url or not gcs_path:
                # Clean up temp file
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                return False, entry
                
            # Update entry with new information
            entry["gcs_path"] = gcs_path
            entry["url"] = public_url
            entry["size"] = file_size
            entry["directlyDownloaded"] = True
            entry["type"] = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            
            # Update name if we found a better one
            if presentation_name:
                entry["name"] = presentation_name
                
            # Clean up temp file
            os.remove(temp_file_path)
            
            # Update the content in database
            self._update_content_document(content_id, entry)
                
            return True, entry
            
        except Exception as e:
            logger.error(f"Error downloading and storing presentation: {str(e)}", exc_info=True)
            return False, entry

    def _download_file(self, drive_id: Optional[str], export_url: Optional[str], 
                       temp_file_path: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Attempt to download file using various methods.
        
        Args:
            drive_id: Google Drive file ID
            export_url: Direct export URL for the file
            temp_file_path: Path to save downloaded file
            
        Returns:
            Success flag, file metadata if available
        """
        file_metadata = None
        
        # Try Drive API with service account first if we have drive_id
        if drive_id:
            try:
                from app.services.drive_service import build_drive_service
                drive_service = build_drive_service()
                
                # Try download with Drive API
                mime_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
                success = drive_service.download_large_file(drive_id, temp_file_path, mime_type)
                
                if success:
                    # Get file metadata
                    try:
                        file_metadata = drive_service.get_file_metadata(drive_id)
                    except Exception:
                        pass
                    return True, file_metadata
            except Exception:
                logger.warning(f"Drive API download failed for ID: {drive_id}", exc_info=True)
        
        # Extract drive ID from export URL if possible and try API download
        if export_url and not drive_id:
            import re
            url_drive_id = None
            if "/presentation/d/" in export_url:
                match = re.search(r"/presentation/d/([^/]+)", export_url)
                if match:
                    url_drive_id = match.group(1)
                    
            if url_drive_id:
                try:
                    from app.services.drive_service import build_drive_service
                    drive_service = build_drive_service()
                    
                    # Try the direct API download with the extracted ID
                    mime_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
                    success = drive_service.download_large_file(url_drive_id, temp_file_path, mime_type)
                    
                    if success:
                        # Get file metadata
                        try:
                            file_metadata = drive_service.get_file_metadata(url_drive_id)
                        except Exception:
                            pass
                        return True, file_metadata
                except Exception:
                    logger.warning(f"Drive API download failed for URL-extracted ID: {url_drive_id}")
        
        # If Drive API methods failed, try with direct export URL
        if export_url:
            try:
                from app.services.drive_service import build_drive_service
                drive_service = build_drive_service()
                
                success, _ = drive_service._download_with_direct_export_url(export_url, temp_file_path)
                if success:
                    return True, file_metadata
            except Exception:
                logger.warning(f"Authenticated direct URL download failed")
        
        # Last resort: try multiple download methods in sequence
        download_methods = [
            self._download_with_urllib,
            self._download_with_range_headers,
            self._download_with_cookie_auth
        ]
        
        for download_method in download_methods:
            try:
                success = download_method(export_url, temp_file_path)
                if success and os.path.exists(temp_file_path) and os.path.getsize(temp_file_path) > 0:
                    return True, file_metadata
            except Exception:
                continue
                
        return False, None
    
    def _upload_to_storage(self, file_path: str, filename: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Upload file to cloud storage bucket.
        
        Args:
            file_path: Path to local file
            filename: Name for storage
            
        Returns:
            Public URL, GCS path
        """
        try:
            if not self.bucket:
                logger.error("No GCS bucket available for upload")
                return None, None
                
            # Create blob path with folder prefix
            bucket_name = os.environ.get("GCS_BUCKET_NAME")
            folder_prefix = os.environ.get("GCS_FOLDER_PREFIX", "uploads")
            storage_filename = f"{uuid.uuid4()}.pptx"
            blob_path = f"{folder_prefix}/{storage_filename}"
            
            # Get the bucket
            blob = self.bucket.blob(blob_path)
            
            # Upload file with content type
            mime_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            blob.upload_from_filename(file_path, content_type=mime_type)
            
            # Generate URL for access
            if os.environ.get("GCS_MAKE_PUBLIC", "").lower() == "true":
                blob.make_public()
                public_url = blob.public_url
            else:
                # Generate a signed URL that expires after a period
                expiration = int(os.environ.get("GCS_URL_EXPIRATION", "86400"))  # Default 24 hours
                public_url = blob.generate_signed_url(version="v4", expiration=expiration, method="GET")
                
            # Set GCS path
            gcs_path = f"gs://{bucket_name}/{blob_path}"
            
            return public_url, gcs_path
            
        except Exception as e:
            logger.error(f"Failed to upload file to bucket: {str(e)}", exc_info=True)
            return None, None
    
    def _update_content_document(self, content_id: str, entry: Dict[str, Any]) -> bool:
        """
        Update content document with new file information.
        
        Args:
            content_id: Content document ID
            entry: Updated file entry
            
        Returns:
            Success flag
        """
        try:
            if not self.firestore:
                logger.warning("No Firestore client available for document update")
                return False
                
            # Get the existing content
            content = self.firestore.get_document("content", content_id)
            if not content:
                logger.error(f"Content document not found: {content_id}")
                return False
                
            # Update the fileUrls entry
            updated = False
            for i, url_entry in enumerate(content.get("fileUrls", [])):
                if url_entry.get("presentation_type") == entry.get("presentation_type"):
                    content["fileUrls"][i] = entry
                    updated = True
                    break
                    
            # If not found, append it
            if not updated and entry.get("presentation_type"):
                content["fileUrls"].append(entry)
                
            # If presentation_type is presentation_slides, update presentationSlidesUrl
            if entry.get("presentation_type") == "presentation_slides":
                content["presentationSlidesUrl"] = entry.get("url")
                
            # If presentation_type is recap_slides, update recapSlidesUrl
            if entry.get("presentation_type") == "recap_slides":
                content["recapSlidesUrl"] = entry.get("url")
                
            # Update the document
            self.firestore.update_document("content", content_id, content)
            return True
            
        except Exception as e:
            logger.error(f"Failed to update content in database: {str(e)}", exc_info=True)
            return False
    
    # Helper download methods
    def _download_with_urllib(self, url: str, file_path: str, max_retries: int = 3) -> bool:
        """Download a file using urllib with retries."""
        for attempt in range(max_retries):
            try:
                urllib.request.urlretrieve(url, file_path)
                
                if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                    return True
            except Exception:
                if attempt < max_retries - 1:
                    # Exponential backoff with a bit of randomness
                    sleep_time = (2 ** attempt) + (random.random() * 2)
                    time.sleep(sleep_time)
        
        return False

    def _download_with_range_headers(self, url: str, file_path: str, 
                                     chunk_size: int = 16777216, 
                                     max_retries: int = 3) -> bool:
        """Download a file using range headers for chunked download."""
        try:
            head_response = requests.head(url, timeout=30)
            content_length = int(head_response.headers.get('Content-Length', 0))
        except Exception:
            content_length = 1000000000  # Assume a large file (1GB)
        
        # Calculate chunks
        chunks = []
        for i in range(0, content_length, chunk_size):
            chunks.append((i, min(i + chunk_size - 1, content_length - 1)))
        
        # Download each chunk with retries
        with open(file_path, 'wb') as f:
            for chunk_start, chunk_end in chunks:
                success = False
                for attempt in range(max_retries):
                    try:
                        headers = {'Range': f'bytes={chunk_start}-{chunk_end}'}
                        response = requests.get(url, headers=headers, timeout=60)
                        
                        if response.status_code in [200, 206]:
                            f.write(response.content)
                            f.flush()
                            success = True
                            break
                    except Exception:
                        if attempt < max_retries - 1:
                            sleep_time = (2 ** attempt) + (random.random() * 2)
                            time.sleep(sleep_time)
                
                if not success:
                    return False
        
        return os.path.exists(file_path) and os.path.getsize(file_path) > 0

    def _download_with_cookie_auth(self, url: str, file_path: str, max_retries: int = 3) -> bool:
        """Download a file using requests with cookie-based authentication."""
        # Get auth cookie from environment
        auth_cookie = os.environ.get("GDRIVE_AUTH_COOKIE", "")
        if not auth_cookie:
            return False
        
        for attempt in range(max_retries):
            try:
                # Set up headers with cookies
                headers = {
                    'Cookie': auth_cookie,
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                # Use stream=True to avoid loading entire file into memory
                response = requests.get(url, headers=headers, stream=True, timeout=60)
                
                if response.status_code == 200:
                    # Download in chunks to file
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    return os.path.exists(file_path) and os.path.getsize(file_path) > 0
            except Exception:
                if attempt < max_retries - 1:
                    sleep_time = (2 ** attempt) + (random.random() * 2)
                    time.sleep(sleep_time)
        
        return False 