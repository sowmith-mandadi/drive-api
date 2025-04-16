"""
Service for batch job operations.
"""
import logging
from datetime import datetime
from typing import List, Optional

from app.models.batch import BatchJob, BatchJobCreate, BatchJobError, BatchJobStatus, BatchJobUpdate
from app.repositories.batch_repository import BatchRepository

# Setup logging
logger = logging.getLogger(__name__)


class BatchService:
    """Service for batch job operations."""

    def __init__(self) -> None:
        """Initialize the batch service."""
        self.repository = BatchRepository()

    def get_all_jobs(self, limit: int = 100, offset: int = 0) -> List[BatchJob]:
        """Get all batch jobs with pagination.

        Args:
            limit: Maximum number of jobs to return.
            offset: Number of jobs to skip.

        Returns:
            List of batch jobs.
        """
        return self.repository.get_all(limit=limit, offset=offset)

    def get_job_by_id(self, job_id: str) -> Optional[BatchJob]:
        """Get batch job by ID.

        Args:
            job_id: ID of the batch job.

        Returns:
            BatchJob or None if not found.
        """
        return self.repository.get_by_id(job_id)

    def create_job(self, job_data: BatchJobCreate) -> Optional[BatchJob]:
        """Create a new batch job.

        Args:
            job_data: Batch job creation data.

        Returns:
            Created batch job or None if failed.
        """
        return self.repository.create(job_data)

    def update_job(self, job_id: str, update_data: BatchJobUpdate) -> Optional[BatchJob]:
        """Update an existing batch job.

        Args:
            job_id: ID of the batch job to update.
            update_data: Batch job update data.

        Returns:
            Updated batch job or None if not found or failed.
        """
        return self.repository.update(job_id, update_data)

    def delete_job(self, job_id: str) -> bool:
        """Delete a batch job.

        Args:
            job_id: ID of the batch job to delete.

        Returns:
            True if deleted, False if not found or failed.
        """
        return self.repository.delete(job_id)

    def update_job_progress(
        self,
        job_id: str,
        processed: int = 1,
        successful: int = 0,
        failed: int = 0,
        error: Optional[BatchJobError] = None,
    ) -> Optional[BatchJob]:
        """Update batch job progress.

        Args:
            job_id: ID of the batch job.
            processed: Number of newly processed items.
            successful: Number of newly successful items.
            failed: Number of newly failed items.
            error: Optional error to add.

        Returns:
            Updated batch job or None if not found or failed.
        """
        job = self.get_job_by_id(job_id)
        if not job:
            return None

        # Prepare update data
        update_data = BatchJobUpdate(
            processed_items=job.processed_items + processed,
            successful_items=job.successful_items + successful,
            failed_items=job.failed_items + failed,
        )

        # Add error if provided
        if error:
            errors = job.errors.copy()
            errors.append(error)
            update_data.errors = errors

        # Update job
        return self.update_job(job_id, update_data)

    def mark_job_completed(self, job_id: str) -> Optional[BatchJob]:
        """Mark a batch job as completed.

        Args:
            job_id: ID of the batch job.

        Returns:
            Updated batch job or None if not found or failed.
        """
        job = self.get_job_by_id(job_id)
        if not job:
            return None

        # Determine final status based on success/failure rate
        final_status = BatchJobStatus.COMPLETED
        if job.failed_items > 0 and job.successful_items == 0:
            final_status = BatchJobStatus.FAILED
        elif job.failed_items > 0:
            # Partial success
            final_status = BatchJobStatus.COMPLETED

        # Prepare update data
        update_data = BatchJobUpdate(
            status=final_status,
            completed_at=datetime.now(),
        )

        # Update job
        return self.update_job(job_id, update_data)

    def mark_job_failed(self, job_id: str, error_message: str) -> Optional[BatchJob]:
        """Mark a batch job as failed with an error message.

        Args:
            job_id: ID of the batch job.
            error_message: Error message.

        Returns:
            Updated batch job or None if not found or failed.
        """
        job = self.get_job_by_id(job_id)
        if not job:
            return None

        # Create a general error (not tied to a specific row)
        error = BatchJobError(row=-1, message=error_message)

        # Prepare update data
        errors = job.errors.copy()
        errors.append(error)

        update_data = BatchJobUpdate(
            status=BatchJobStatus.FAILED,
            errors=errors,
            completed_at=datetime.now(),
        )

        # Update job
        return self.update_job(job_id, update_data)

    def mark_job_processing(self, job_id: str) -> Optional[BatchJob]:
        """Mark a batch job as processing.

        Args:
            job_id: ID of the batch job.

        Returns:
            Updated batch job or None if not found or failed.
        """
        update_data = BatchJobUpdate(
            status=BatchJobStatus.PROCESSING,
        )
        return self.update_job(job_id, update_data)
