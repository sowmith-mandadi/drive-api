"""
Repository for batch job operations.
"""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.db.firestore_client import FirestoreClient
from app.models.batch import BatchJob, BatchJobCreate, BatchJobStatus, BatchJobUpdate

# Setup logging
logger = logging.getLogger(__name__)


class BatchRepository:
    """Repository for batch job database operations."""

    def __init__(self) -> None:
        """Initialize the batch repository."""
        self.firestore = FirestoreClient()
        self.collection = "batch_jobs"

    def get_all(self, limit: int = 100, offset: int = 0) -> List[BatchJob]:
        """Get all batch jobs with pagination.

        Args:
            limit: Maximum number of items to return.
            offset: Number of items to skip.

        Returns:
            List of batch jobs.
        """
        docs = self.firestore.list_documents(
            self.collection, limit=limit, offset=offset, order_by="-created_at"
        )
        return [self._to_batch_model(doc) for doc in docs]

    def get_by_id(self, job_id: str) -> Optional[BatchJob]:
        """Get batch job by ID.

        Args:
            job_id: ID of the batch job.

        Returns:
            BatchJob or None if not found.
        """
        doc = self.firestore.get_document(self.collection, job_id)
        if not doc:
            return None
        return self._to_batch_model(doc)

    def create(self, job_data: BatchJobCreate) -> Optional[BatchJob]:
        """Create a new batch job.

        Args:
            job_data: Batch job creation data.

        Returns:
            Created batch job or None if failed.
        """
        try:
            # Generate ID
            job_id = self.firestore.generate_id()

            # Prepare data
            now = datetime.now().isoformat()

            # Create batch job object
            job_dict = {
                "id": job_id,
                "status": BatchJobStatus.PENDING.value,
                "job_type": job_data.job_type,
                "total_items": job_data.total_items,
                "processed_items": 0,
                "successful_items": 0,
                "failed_items": 0,
                "errors": [],
                "metadata": job_data.metadata or {},
                "created_at": now,
                "updated_at": now,
                "created_by": job_data.created_by,
            }

            # Create in Firestore
            success = self.firestore.create_document(self.collection, job_id, job_dict)

            if not success:
                return None

            # Get the created job
            created_job = self.get_by_id(job_id)
            return created_job

        except Exception as e:
            logger.error(f"Error creating batch job: {str(e)}")
            return None

    def update(self, job_id: str, update_data: BatchJobUpdate) -> Optional[BatchJob]:
        """Update an existing batch job.

        Args:
            job_id: ID of the batch job to update.
            update_data: Batch job update data.

        Returns:
            Updated batch job or None if not found or failed.
        """
        try:
            # Check if job exists
            existing_job = self.get_by_id(job_id)
            if not existing_job:
                return None

            # Prepare update data
            update_dict: Dict[str, Any] = {"updated_at": datetime.now().isoformat()}

            if update_data.status is not None:
                update_dict["status"] = update_data.status.value
            if update_data.processed_items is not None:
                update_dict["processed_items"] = update_data.processed_items
            if update_data.successful_items is not None:
                update_dict["successful_items"] = update_data.successful_items
            if update_data.failed_items is not None:
                update_dict["failed_items"] = update_data.failed_items
            if update_data.errors is not None:
                update_dict["errors"] = [error.dict() for error in update_data.errors]
            if update_data.metadata is not None:
                update_dict["metadata"] = update_data.metadata
            if update_data.completed_at is not None:
                update_dict["completed_at"] = update_data.completed_at.isoformat()

            # Update in Firestore
            success = self.firestore.update_document(self.collection, job_id, update_dict)

            if not success:
                return None

            # Get the updated job
            updated_job = self.get_by_id(job_id)
            return updated_job

        except Exception as e:
            logger.error(f"Error updating batch job: {str(e)}")
            return None

    def delete(self, job_id: str) -> bool:
        """Delete a batch job.

        Args:
            job_id: ID of the batch job to delete.

        Returns:
            True if deleted, False if not found or failed.
        """
        return self.firestore.delete_document(self.collection, job_id)

    def _to_batch_model(self, doc: Dict[str, Any]) -> BatchJob:
        """Convert a Firestore document to a BatchJob model.

        Args:
            doc: Firestore document data.

        Returns:
            BatchJob model.
        """
        # Convert string dates to datetime objects
        created_at = doc.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        else:
            created_at = datetime.now()

        updated_at = doc.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        else:
            updated_at = datetime.now()

        completed_at = doc.get("completed_at")
        if isinstance(completed_at, str):
            completed_at = datetime.fromisoformat(completed_at)
        else:
            completed_at = None

        # Get document ID
        doc_id = doc.get("id") or ""

        # Convert status string to enum
        status_str = doc.get("status", BatchJobStatus.PENDING.value)
        try:
            status = BatchJobStatus(status_str)
        except ValueError:
            status = BatchJobStatus.PENDING

        # Create BatchJob model
        return BatchJob(
            id=doc_id,
            status=status,
            job_type=doc.get("job_type", ""),
            total_items=doc.get("total_items", 0),
            processed_items=doc.get("processed_items", 0),
            successful_items=doc.get("successful_items", 0),
            failed_items=doc.get("failed_items", 0),
            errors=doc.get("errors", []),
            metadata=doc.get("metadata", {}),
            created_at=created_at,
            updated_at=updated_at,
            completed_at=completed_at,
            created_by=doc.get("created_by"),
        )
