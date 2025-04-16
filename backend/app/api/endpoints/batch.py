"""
API endpoints for batch job operations.
"""
import json
import os
from datetime import datetime
from typing import List, Optional

import pandas as pd
from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile, status

from app.core.logging import configure_logging
from app.models.batch import BatchJob, BatchJobCreate, BatchJobError, BatchJobStatus, BatchJobUpdate
from app.services.batch_service import BatchService
from app.services.content_processor import ContentProcessor
from app.services.task_service import TaskService

# Setup logging
logger = configure_logging()

router = APIRouter(prefix="/batch", tags=["Batch Operations"])

# Service instances
batch_service = BatchService()
task_service = TaskService()
content_processor = ContentProcessor()


@router.get("/jobs", response_model=List[BatchJob])
async def list_batch_jobs(limit: int = 100, offset: int = 0):
    """List all batch jobs with pagination."""
    jobs = batch_service.get_all_jobs(limit=limit, offset=offset)
    return jobs


@router.get("/jobs/{job_id}", response_model=BatchJob)
async def get_batch_job(job_id: str):
    """Get a specific batch job by ID."""
    job = batch_service.get_job_by_id(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Batch job with ID {job_id} not found"
        )
    return job


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def bulk_upload_content(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: Optional[str] = Form(None),
):
    """
    Upload a batch of content items via a CSV or Excel file.

    The file should contain columns matching the content metadata fields.
    Each row will be processed asynchronously and stored in the database.
    """
    try:
        # Validate file type
        file_extension = os.path.splitext(file.filename)[1].lower() if file.filename else ""
        if file_extension not in [".csv", ".xlsx", ".xls"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a CSV or Excel file",
            )

        # Create a temporary file to store the uploaded content
        temp_file_path = os.path.join(os.getcwd(), "uploads", "temp", file.filename)
        os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)

        # Save the uploaded file
        with open(temp_file_path, "wb") as f:
            contents = await file.read()
            f.write(contents)

        # Read the file using pandas
        try:
            if file_extension == ".csv":
                df = pd.read_csv(temp_file_path)
            else:  # Excel file
                df = pd.read_excel(temp_file_path)
        except Exception as e:
            os.remove(temp_file_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error reading file: {str(e)}",
            )

        # Validate required columns
        required_columns = ["title", "track", "sessionType"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            os.remove(temp_file_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {', '.join(missing_columns)}",
            )

        # Check if we have any rows
        if df.empty:
            os.remove(temp_file_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File contains no data rows",
            )

        # Create a batch job
        job_data = BatchJobCreate(
            job_type="content_upload",
            total_items=len(df),
            metadata={
                "filename": file.filename,
                "total_rows": len(df),
            },
            created_by=user_id,
        )

        batch_job = batch_service.create_job(job_data)
        if not batch_job:
            os.remove(temp_file_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create batch job",
            )

        # Start processing in background
        background_tasks.add_task(
            process_batch_upload,
            batch_job.id,
            temp_file_path,
            file_extension,
        )

        return {
            "job_id": batch_job.id,
            "status": batch_job.status,
            "total_items": batch_job.total_items,
            "message": "Batch upload initiated",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch upload failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process batch upload: {str(e)}",
        )


@router.delete("/jobs/{job_id}")
async def delete_batch_job(job_id: str):
    """Delete a batch job."""
    job = batch_service.get_job_by_id(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Batch job with ID {job_id} not found"
        )

    # Only allow deletion of completed or failed jobs
    if job.status not in [
        BatchJobStatus.COMPLETED,
        BatchJobStatus.FAILED,
        BatchJobStatus.CANCELLED,
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete job with status {job.status}",
        )

    success = batch_service.delete_job(job_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete batch job",
        )

    return {"message": f"Batch job with ID {job_id} deleted"}


@router.post("/jobs/{job_id}/cancel")
async def cancel_batch_job(job_id: str):
    """Cancel a batch job."""
    job = batch_service.get_job_by_id(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Batch job with ID {job_id} not found"
        )

    # Only allow cancellation of pending or processing jobs
    if job.status not in [BatchJobStatus.PENDING, BatchJobStatus.PROCESSING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel job with status {job.status}",
        )

    # Update job status
    update_data = BatchJobUpdate(
        status=BatchJobStatus.CANCELLED,
        completed_at=datetime.now(),
    )

    updated_job = batch_service.update_job(job_id, update_data)
    if not updated_job:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel batch job",
        )

    return {"message": f"Batch job with ID {job_id} cancelled"}


async def process_batch_upload(job_id: str, file_path: str, file_extension: str):
    """
    Process a batch upload file.

    Args:
        job_id: ID of the batch job.
        file_path: Path to the uploaded file.
        file_extension: File extension.
    """
    try:
        # Update job status to processing
        batch_service.mark_job_processing(job_id)

        # Read the file using pandas
        try:
            if file_extension == ".csv":
                df = pd.read_csv(file_path)
            else:  # Excel file
                df = pd.read_excel(file_path)
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {str(e)}")
            batch_service.mark_job_failed(job_id, f"Failed to read file: {str(e)}")
            if os.path.exists(file_path):
                os.remove(file_path)
            return

        # Keep track of success/failure
        total_rows = len(df)
        processed_rows = 0
        successful_rows = 0
        failed_rows = 0

        # Process each row
        for index, row in df.iterrows():
            try:
                # Convert row to dict and handle NaN values
                row_dict = row.to_dict()
                row_dict = {k: (v if not pd.isna(v) else None) for k, v in row_dict.items()}

                # Parse lists and objects from strings if needed
                for key, value in row_dict.items():
                    if isinstance(value, str):
                        if value.startswith("[") and value.endswith("]"):
                            try:
                                row_dict[key] = json.loads(value)
                            except json.JSONDecodeError:
                                try:
                                    # Replace single quotes with double quotes
                                    fixed_value = value.replace("'", '"')
                                    row_dict[key] = json.loads(fixed_value)
                                except Exception as e:
                                    # If still fails, leave as is
                                    pass
                        elif value.startswith("{") and value.endswith("}"):
                            try:
                                row_dict[key] = json.loads(value)
                            except json.JSONDecodeError:
                                try:
                                    # Replace single quotes with double quotes
                                    fixed_value = value.replace("'", '"')
                                    row_dict[key] = json.loads(fixed_value)
                                except Exception as e:
                                    # If still fails, leave as is
                                    pass

                # Handle presenters if present
                presenters = row_dict.get("presenters", [])
                if isinstance(presenters, str):
                    try:
                        presenters = json.loads(presenters)
                    except json.JSONDecodeError:
                        try:
                            # Replace single quotes with double quotes
                            fixed_value = presenters.replace("'", '"')
                            presenters = json.loads(fixed_value)
                        except Exception as e:
                            # If all parsing fails, create an empty list
                            presenters = []
                # Ensure presenters is a list
                if not isinstance(presenters, list):
                    presenters = []

                # Handle tags if present
                tags = row_dict.get("tags", [])
                if isinstance(tags, str):
                    try:
                        tags = json.loads(tags)
                    except json.JSONDecodeError:
                        try:
                            # Replace single quotes with double quotes
                            fixed_value = tags.replace("'", '"')
                            tags = json.loads(fixed_value)
                        except Exception as e:
                            # Split by comma if it's a comma-separated string
                            if "," in tags:
                                tags = [tag.strip() for tag in tags.split(",")]
                            else:
                                tags = [tags]  # Treat as a single tag
                # Ensure tags is a list
                if not isinstance(tags, list):
                    tags = [str(tags)]

                # Prepare content data
                content_data = {
                    "title": row_dict.get("title", ""),
                    "description": row_dict.get("description", ""),
                    "track": row_dict.get("track", ""),
                    "tags": tags,
                    "sessionType": row_dict.get("sessionType", ""),
                    "sessionDate": row_dict.get("sessionDate"),
                    "learningLevel": row_dict.get("learningLevel"),
                    "topic": row_dict.get("topic"),
                    "jobRole": row_dict.get("jobRole"),
                    "areaOfInterest": row_dict.get("areaOfInterest"),
                    "industry": row_dict.get("industry"),
                    "presenters": presenters,
                    "used": False,
                }

                # Process file URL if present
                file_url = row_dict.get("fileUrl")

                # Process the content item
                success, message, created_content = await content_processor.process_content_item(
                    content_data, file_url
                )

                # Update progress
                processed_rows += 1

                if success:
                    successful_rows += 1
                    batch_service.update_job_progress(job_id, processed=1, successful=1)
                else:
                    failed_rows += 1
                    error = BatchJobError(
                        row=index,
                        message=message,
                        details=row_dict,
                    )
                    batch_service.update_job_progress(job_id, processed=1, failed=1, error=error)

            except Exception as e:
                # Log error
                logger.error(f"Error processing row {index}: {str(e)}")

                # Create error record
                error = BatchJobError(
                    row=index,
                    message=f"Failed to process row: {str(e)}",
                    details=row.to_dict(),
                )

                # Update progress
                processed_rows += 1
                failed_rows += 1

                # Update job progress with error
                batch_service.update_job_progress(job_id, processed=1, failed=1, error=error)

            # Progress updates every 10 rows (or configure as needed)
            if processed_rows % 10 == 0:
                logger.info(f"Processed {processed_rows}/{total_rows} rows")

        # Mark job as completed
        batch_service.mark_job_completed(job_id)

        # Clean up
        if os.path.exists(file_path):
            os.remove(file_path)

        logger.info(f"Batch upload completed: {successful_rows} successful, {failed_rows} failed")

    except Exception as e:
        logger.error(f"Batch processing failed: {str(e)}")

        # Mark job as failed
        batch_service.mark_job_failed(job_id, str(e))

        # Clean up
        if os.path.exists(file_path):
            os.remove(file_path)
