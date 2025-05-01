"""
Service for processing content items from bulk uploads.
"""
import os
import shutil
import uuid
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import requests

from app.core.logging import configure_logging
from app.db.firestore_client import FirestoreClient

# Setup logging
logger = configure_logging()


class ContentProcessor:
    """Service for processing content items from bulk uploads."""

    def __init__(self) -> None:
        """Initialize the content processor."""
        self.firestore = FirestoreClient()

        # Use environment variables if set, otherwise use defaults
        base_upload_dir = os.environ.get("TEMP_UPLOAD_DIR", os.path.join(os.getcwd(), "uploads"))
        self.temp_dir = os.environ.get("TEMP_PROCESSING_DIR", os.path.join(base_upload_dir, "temp"))
        self.bucket_dir = os.environ.get(
            "UPLOAD_BUCKET_DIR", os.path.join(base_upload_dir, "bucket")
        )

        # Create directories
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.bucket_dir, exist_ok=True)

        logger.info(f"Using temp directory: {self.temp_dir}")
        logger.info(f"Using bucket directory: {self.bucket_dir}")

    async def process_content_item(
        self, content_data: Dict[str, Any], file_url: Optional[str] = None
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Process a content item from bulk upload.

        Args:
            content_data: Content metadata.
            file_url: Optional URL to download file from.

        Returns:
            Tuple of (success, message, created_content).
        """
        try:
            # Generate ID
            content_id = self.firestore.generate_id()

            # Set basic fields
            now = datetime.now().isoformat()
            content_data["id"] = content_id
            content_data["dateCreated"] = now
            content_data["dateModified"] = now
            content_data["fileUrls"] = []
            content_data["driveUrls"] = []

            # Process file if URL provided
            if file_url and isinstance(file_url, str) and file_url.strip():
                # Clean up URL
                file_url = file_url.strip()

                # Only process if it looks like a valid URL
                if file_url.startswith(("http://", "https://", "ftp://")):
                    success, message, file_info = await self._process_file_from_url(
                        content_id, file_url
                    )
                    if success and file_info:
                        content_data["fileUrls"].append(file_info)

            # Store in Firestore
            success = self.firestore.create_document("content", content_id, content_data)
            if not success:
                return False, "Failed to store content metadata", None

            return True, "Content created successfully", content_data

        except Exception as e:
            logger.error(f"Error processing content item: {str(e)}")
            return False, f"Error processing content: {str(e)}", None

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

            # Destination in the bucket
            destination_path = os.path.join(self.bucket_dir, storage_filename)

            # Move file to bucket
            try:
                shutil.copy2(temp_file_path, destination_path)

                # Delete the temporary file
                os.remove(temp_file_path)
            except Exception as e:
                logger.error(f"Failed to move file to bucket: {str(e)}")
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                return False, f"Failed to store file: {str(e)}", None

            # Generate public URL
            public_url = f"/api/files/{storage_filename}"

            # Return file info
            file_info = {
                "url": public_url,
                "name": file_name,
                "type": content_type,
                "size": file_size,
            }

            return True, "File processed successfully", file_info

        except Exception as e:
            logger.error(f"Error processing file from URL: {str(e)}")
            # Clean up any temp file
            if "temp_file_path" in locals() and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            return False, f"Error processing file: {str(e)}", None
