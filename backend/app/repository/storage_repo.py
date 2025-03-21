"""Google Cloud Storage repository for file storage."""

import os
import uuid
import logging
import tempfile
from typing import Optional, List, Dict, Any
from werkzeug.datastructures import FileStorage
from google.cloud import storage

# Initialize logger
logger = logging.getLogger(__name__)

class StorageRepository:
    """Repository for Google Cloud Storage operations."""
    
    def __init__(self):
        """Initialize the storage repository."""
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize Google Cloud Storage client."""
        try:
            self.storage_client = storage.Client.from_service_account_json('credentials.json')
            bucket_name = os.getenv('GCS_BUCKET_NAME', 'conference-content-bucket')
            
            # Get or create bucket
            if self.storage_client.lookup_bucket(bucket_name):
                self.bucket = self.storage_client.bucket(bucket_name)
            else:
                self.bucket = self.storage_client.create_bucket(bucket_name)
                
            self.initialized = True
            logger.info(f"Connected to GCS bucket: {bucket_name}")
        except Exception as e:
            logger.error(f"Error connecting to Google Cloud Storage: {e}")
            self.bucket = None
            self.initialized = False
    
    def store_file(self, file: FileStorage, content_id: str) -> Optional[str]:
        """Store a file in Google Cloud Storage.
        
        Args:
            file: The file to store
            content_id: The ID of the content
            
        Returns:
            Optional[str]: Public URL of the stored file or None if storage failed
        """
        if not self.initialized or not file:
            logger.warning("Storage not initialized or no file provided")
            return None
        
        try:
            # Create a unique filename
            file_extension = os.path.splitext(file.filename)[1] if "." in file.filename else ""
            unique_filename = f"{content_id}/{uuid.uuid4()}{file_extension}"
            
            # Save the file temporarily
            temp_file_path = self.save_temp_file(file)
            
            # Upload to GCS
            blob = self.bucket.blob(unique_filename)
            blob.upload_from_filename(temp_file_path)
            
            # Make the file publicly accessible
            blob.make_public()
            
            # Clean up temporary file
            os.remove(temp_file_path)
            
            logger.info(f"File {file.filename} stored as {unique_filename}")
            return blob.public_url
        except Exception as e:
            logger.error(f"Error storing file in GCS: {e}")
            return None
    
    def save_temp_file(self, file: FileStorage) -> str:
        """Save a file to a temporary location.
        
        Args:
            file: The file to save
            
        Returns:
            str: Path to the temporary file
        """
        try:
            # Create a temporary file
            temp_dir = tempfile.gettempdir()
            temp_filename = f"{uuid.uuid4()}_{file.filename}"
            temp_file_path = os.path.join(temp_dir, temp_filename)
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
            
            # Save the file
            file.save(temp_file_path)
            
            return temp_file_path
        except Exception as e:
            logger.error(f"Error saving temporary file: {e}")
            return ""
    
    def remove_temp_file(self, file_path: str) -> bool:
        """Remove a temporary file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            bool: Success status
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing temporary file: {e}")
            return False
    
    def get_file_url(self, blob_name: str) -> Optional[str]:
        """Get the public URL for a file.
        
        Args:
            blob_name: Name of the blob in the bucket
            
        Returns:
            Optional[str]: Public URL of the file
        """
        if not self.initialized:
            logger.warning("Storage not initialized")
            return None
        
        try:
            blob = self.bucket.blob(blob_name)
            blob.make_public()
            return blob.public_url
        except Exception as e:
            logger.error(f"Error getting file URL: {e}")
            return None
    
    def delete_file(self, blob_name: str) -> bool:
        """Delete a file from storage.
        
        Args:
            blob_name: Name of the blob in the bucket
            
        Returns:
            bool: Success status
        """
        if not self.initialized:
            logger.warning("Storage not initialized")
            return False
        
        try:
            blob = self.bucket.blob(blob_name)
            blob.delete()
            logger.info(f"File {blob_name} deleted")
            return True
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False 