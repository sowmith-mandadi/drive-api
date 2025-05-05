"""
Service for handling background tasks and Cloud Tasks.
"""
import os
import shutil
import uuid
from typing import Any, Dict

from google.cloud import storage, tasks_v2

from app.core.config import settings
from app.core.logging import configure_logging
from app.db.firestore_client import FirestoreClient

# Setup logging
logger = configure_logging()


class TaskService:
    """Service for handling background tasks and Cloud Tasks."""

    def __init__(self) -> None:
        """Initialize the task service."""
        try:
            logger.info("Initializing TaskService")

            # Initialize Firestore client
            try:
                self.firestore = FirestoreClient()
                logger.info("TaskService: Firestore client initialized successfully")
            except Exception as db_error:
                logger.error(
                    f"TaskService: Failed to initialize Firestore client: {str(db_error)}",
                    exc_info=True,
                )
                # Re-raise to fail initialization
                raise

            # Use environment variables with proper defaults for App Engine
            # Default to /tmp paths which are writable in App Engine
            self.temp_dir = os.environ.get("TEMP_PROCESSING_DIR", "/tmp/processing")
            os.makedirs(self.temp_dir, exist_ok=True)
            logger.info(f"TaskService using temp directory: {self.temp_dir}")

            # Initialize GCS client if configured
            self.storage_client = None
            self.bucket = None
            self.use_gcs = settings.USE_GCS

            if self.use_gcs:
                try:
                    self.storage_client = storage.Client()
                    self.bucket = self.storage_client.bucket(settings.GCS_BUCKET_NAME)
                    logger.info(
                        f"TaskService: GCS client initialized with bucket {settings.GCS_BUCKET_NAME}"
                    )
                except Exception as gcs_error:
                    logger.error(
                        f"TaskService: Failed to initialize GCS client: {str(gcs_error)}",
                        exc_info=True,
                    )
                    # Don't re-raise - we can continue without GCS
                    self.use_gcs = False

            # Fall back to local storage if GCS is not available
            if not self.use_gcs:
                self.bucket_dir = os.environ.get("UPLOAD_BUCKET_DIR", "/tmp/bucket")
                logger.info(f"TaskService using bucket directory: {self.bucket_dir}")
                os.makedirs(self.bucket_dir, exist_ok=True)

            # Initialize Cloud Tasks client if configured
            self.tasks_client = None
            if settings.USE_CLOUD_TASKS:
                try:
                    self.tasks_client = tasks_v2.CloudTasksClient()
                    logger.info("TaskService: Cloud Tasks client initialized")
                except Exception as tasks_error:
                    logger.error(
                        f"TaskService: Failed to initialize Cloud Tasks client: {str(tasks_error)}",
                        exc_info=True,
                    )
                    # Don't re-raise - we can continue without Cloud Tasks
                    logger.warning(
                        "Using TaskService stub implementation - Cloud Tasks not available"
                    )

            logger.info("TaskService initialization completed successfully")

        except Exception as e:
            logger.error(f"Critical error initializing TaskService: {str(e)}", exc_info=True)
            # Re-raise to fail initialization
            raise

    async def process_file(self, task_data: Dict[str, Any]) -> bool:
        """
        Process a file by uploading to GCS and creating a task for the vector processing backend.

        Args:
            task_data: Dictionary containing file processing details.

        Returns:
            True if successful, False otherwise.
        """
        content_id = task_data.get("content_id")
        file_path = task_data.get("file_path")
        file_name = task_data.get("file_name")
        content_type = task_data.get("content_type", "application/octet-stream")

        if not content_id or not file_path or not os.path.exists(file_path):
            logger.error(f"Invalid task data or file not found: {task_data}")
            return False

        try:
            # Generate a unique file name for storage
            file_extension = os.path.splitext(file_path)[1]
            storage_filename = f"{uuid.uuid4()}{file_extension}"

            # Upload to GCS if configured, otherwise use local storage
            public_url = None
            gcs_path = None

            if self.use_gcs and self.storage_client and self.bucket:
                # Upload to Google Cloud Storage
                blob_path = f"{settings.GCS_FOLDER_PREFIX}/{storage_filename}"
                blob = self.bucket.blob(blob_path)

                # Upload file with content type
                blob.upload_from_filename(file_path, content_type=content_type)

                # Generate a public URL for the file
                if settings.GCS_MAKE_PUBLIC:
                    blob.make_public()
                    public_url = blob.public_url
                else:
                    # Generate a signed URL that expires after a period
                    public_url = blob.generate_signed_url(
                        version="v4", expiration=settings.GCS_URL_EXPIRATION, method="GET"
                    )

                # Store GCS path for internal reference
                gcs_path = f"gs://{settings.GCS_BUCKET_NAME}/{blob_path}"
                logger.info(f"File uploaded to GCS: {gcs_path}")

                # Delete the temporary file after upload
                os.remove(file_path)
            else:
                # Local storage fallback
                destination_path = os.path.join(self.bucket_dir, storage_filename)
                shutil.copy2(file_path, destination_path)
                os.remove(file_path)
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
                    "type": content_type,
                    "gcs_path": gcs_path,
                    "source": "upload",
                }
            )

            # Update Firestore document
            update_data = {"fileUrls": file_urls, "status": "processing"}
            success = self.firestore.update_document("content", content_id, update_data)
            if not success:
                logger.error(f"Failed to update content metadata: {content_id}")
                return False

            # Create a task for vector processing backend
            if settings.USE_CLOUD_TASKS and self.tasks_client:
                self.create_vector_processing_task(
                    {
                        "content_id": content_id,
                        "gcs_path": gcs_path,
                        "file_url": public_url,
                        "file_name": file_name,
                        "content_type": content_type,
                    }
                )
            else:
                logger.info(f"Would create task for vector processing: {content_id}")

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

    def create_vector_processing_task(self, task_data: Dict[str, Any]) -> bool:
        """
        Create a Cloud Task for vector processing by the second backend.

        Args:
            task_data: Dictionary containing processing details.

        Returns:
            True if task created successfully, False otherwise.
        """
        try:
            if not settings.USE_CLOUD_TASKS or not self.tasks_client:
                logger.info(f"Would create task for vector processing: {task_data}")
                return True

            # Prepare the task
            parent = self.tasks_client.queue_path(
                settings.GCP_PROJECT_ID, settings.GCP_LOCATION, settings.VECTOR_PROCESSING_QUEUE
            )

            # Prepare the request body
            import json
            from datetime import datetime, timedelta

            from google.protobuf import duration_pb2, timestamp_pb2

            # Convert task data to JSON
            task_body = json.dumps(task_data).encode()

            # Create the task with appropriate headers
            task = {
                "http_request": {
                    "http_method": tasks_v2.HttpMethod.POST,
                    "url": settings.VECTOR_PROCESSING_ENDPOINT,
                    "headers": {"Content-type": "application/json"},
                    "body": task_body,
                },
                # Set dispatch deadline (optional)
                "dispatch_deadline": duration_pb2.Duration(seconds=settings.TASK_DISPATCH_DEADLINE),
            }

            # Add scheduling time if needed
            if settings.TASK_SCHEDULE_DELAY:
                schedule_time = timestamp_pb2.Timestamp()
                schedule_time.FromDatetime(
                    datetime.utcnow() + timedelta(seconds=settings.TASK_SCHEDULE_DELAY)
                )
                task["schedule_time"] = schedule_time

            # Create the task
            response = self.tasks_client.create_task(request={"parent": parent, "task": task})
            logger.info(f"Vector processing task created: {response.name}")

            return True
        except Exception as e:
            logger.error(f"Error creating vector processing task: {str(e)}")
            return False
