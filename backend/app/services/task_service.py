"""
Service for handling background tasks and Cloud Tasks.
"""
import os
import shutil
import uuid
from typing import Any, Dict

from app.core.logging import configure_logging
from app.db.firestore_client import FirestoreClient

# Setup logging
logger = configure_logging()


class TaskService:
    """Service for handling background tasks and Cloud Tasks."""

    def __init__(self) -> None:
        """Initialize the task service."""
        self.firestore = FirestoreClient()
        self.upload_dir = os.path.join(os.getcwd(), "uploads")
        self.bucket_dir = os.path.join(self.upload_dir, "bucket")
        os.makedirs(self.bucket_dir, exist_ok=True)

    async def process_file(self, task_data: Dict[str, Any]) -> bool:
        """
        Process a file by moving it to the bucket and updating content metadata.

        Args:
            task_data: Dictionary containing file processing details.

        Returns:
            True if successful, False otherwise.
        """
        content_id = task_data.get("content_id")
        file_path = task_data.get("file_path")
        file_name = task_data.get("file_name")

        if not content_id or not file_path or not os.path.exists(file_path):
            logger.error(f"Invalid task data or file not found: {task_data}")
            return False

        try:
            # Generate a unique file name for storage
            file_extension = os.path.splitext(file_path)[1]
            storage_filename = f"{uuid.uuid4()}{file_extension}"

            # Destination in the bucket
            destination_path = os.path.join(self.bucket_dir, storage_filename)

            # Move file to bucket (in production this would upload to a cloud storage bucket)
            shutil.copy2(file_path, destination_path)

            # Delete the temporary file
            os.remove(file_path)

            # Generate a public URL for the file
            # In a real GCP environment, this would be a GCS bucket URL
            public_url = f"/api/files/{storage_filename}"

            # Update content metadata with file URL
            content = self.firestore.get_document("content", content_id)
            if not content:
                logger.error(f"Content not found for ID: {content_id}")
                return False

            # Add file URL to content
            file_urls = content.get("fileUrls", [])
            file_urls.append(
                {
                    "url": public_url,
                    "name": file_name,
                    "type": task_data.get("content_type", "application/octet-stream"),
                }
            )

            # Update Firestore document
            update_data = {"fileUrls": file_urls, "status": "completed"}

            success = self.firestore.update_document("content", content_id, update_data)
            if not success:
                logger.error(f"Failed to update content metadata: {content_id}")
                return False

            logger.info(f"File processed successfully: {content_id}")
            return True

        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")

            # Update content with error status
            error_update = {"status": "error", "error": str(e)}
            self.firestore.update_document("content", content_id, error_update)

            return False

    def create_file_processing_task(self, task_data: Dict[str, Any]) -> bool:
        """
        Create a Cloud Task for file processing.

        Args:
            task_data: Dictionary containing file processing details.

        Returns:
            True if task created successfully, False otherwise.
        """
        try:
            # In a real implementation, this would create a Google Cloud Task
            # For now, just log that we would create a task
            logger.info(f"Would create Cloud Task for file processing: {task_data}")

            # TODO: Implement actual Google Cloud Tasks integration
            # from google.cloud import tasks_v2
            # client = tasks_v2.CloudTasksClient()
            # ...

            return True

        except Exception as e:
            logger.error(f"Error creating file processing task: {str(e)}")
            return False
