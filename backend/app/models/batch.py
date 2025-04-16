"""
Models for batch job processing.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class BatchJobStatus(str, Enum):
    """Status of a batch job."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BatchJobError(BaseModel):
    """Model for batch job processing errors."""

    row: int
    message: str
    details: Optional[Dict[str, Any]] = None


class BatchJob(BaseModel):
    """Model for a batch processing job."""

    id: str
    status: BatchJobStatus = BatchJobStatus.PENDING
    job_type: str  # e.g., "content_upload"
    total_items: int = 0
    processed_items: int = 0
    successful_items: int = 0
    failed_items: int = 0
    errors: List[BatchJobError] = []
    metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    created_by: Optional[str] = None


class BatchJobCreate(BaseModel):
    """Model for creating a batch job."""

    job_type: str
    total_items: int = 0
    metadata: Dict[str, Any] = {}
    created_by: Optional[str] = None


class BatchJobUpdate(BaseModel):
    """Model for updating a batch job."""

    status: Optional[BatchJobStatus] = None
    processed_items: Optional[int] = None
    successful_items: Optional[int] = None
    failed_items: Optional[int] = None
    errors: Optional[List[BatchJobError]] = None
    metadata: Optional[Dict[str, Any]] = None
    completed_at: Optional[datetime] = None
