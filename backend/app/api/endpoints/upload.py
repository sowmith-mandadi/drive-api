"""
API endpoints for file uploads.
"""
import json
import os
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.core.logging import configure_logging
from app.db.firestore_client import FirestoreClient
from app.services.task_service import TaskService

# Setup logging
logger = configure_logging()

router = APIRouter(prefix="/upload", tags=["Upload"])

# Service instances
firestore = FirestoreClient()
task_service = TaskService()


class Presenter(BaseModel):
    """Model for a presenter."""

    id: Optional[str] = None
    name: str
    email: Optional[str] = None
    bio: Optional[str] = None
    photo: Optional[str] = None


class Comment(BaseModel):
    """Model for comments."""

    id: Optional[str] = None
    author: str
    text: str
    dateCreated: Optional[datetime] = None


class ContentUpload(BaseModel):
    """Model for content upload metadata."""

    title: str
    description: str = ""
    track: str
    tags: List[str] = []
    sessionType: str
    sessionDate: Optional[str] = None
    learningLevel: Optional[str] = None
    topic: Optional[str] = None
    jobRole: Optional[str] = None
    areaOfInterest: Optional[str] = None
    industry: Optional[str] = None
    presenters: List[Presenter] = []
    used: Optional[bool] = False
    aiTags: Optional[List[str]] = None


@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_content(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    description: str = Form(""),
    track: str = Form(...),
    tags: str = Form("[]"),  # JSON string of tags
    sessionType: str = Form(...),
    sessionDate: Optional[str] = Form(None),
    learningLevel: Optional[str] = Form(None),
    topic: Optional[str] = Form(None),
    jobRole: Optional[str] = Form(None),
    areaOfInterest: Optional[str] = Form(None),
    industry: Optional[str] = Form(None),
    presenters: str = Form("[]"),  # JSON string of presenters
    file: Optional[UploadFile] = File(None),
):
    """
    Upload a file with metadata.

    The file will be processed asynchronously and stored in a bucket.
    The metadata will be stored in Firestore.
    """
    try:
        # Parse JSON strings
        tags_list = json.loads(tags)
        presenters_list = json.loads(presenters)

        # Generate a new ID
        content_id = firestore.generate_id()

        # Create temp directory for file if it doesn't exist
        temp_dir = os.path.join(os.getcwd(), "uploads", "temp")
        os.makedirs(temp_dir, exist_ok=True)

        # Save file temporarily if provided
        file_path = None
        file_name = None
        if file:
            file_name = file.filename
            file_extension = os.path.splitext(file_name)[1] if file_name else ""
            file_path = os.path.join(temp_dir, f"{content_id}{file_extension}")

            # Save file
            with open(file_path, "wb") as f:
                contents = await file.read()
                f.write(contents)

        # Create content data
        now = datetime.now()
        content_data = {
            "id": content_id,
            "title": title,
            "description": description,
            "track": track,
            "tags": tags_list,
            "sessionType": sessionType,
            "sessionDate": sessionDate,
            "learningLevel": learningLevel,
            "topic": topic,
            "jobRole": jobRole,
            "areaOfInterest": areaOfInterest,
            "industry": industry,
            "presenters": presenters_list,
            "dateCreated": now.isoformat(),
            "dateModified": now.isoformat(),
            "fileUrls": [],
            "driveUrls": [],
            "used": False,
        }

        # Store in Firestore
        success = firestore.create_document("content", content_id, content_data)
        if not success:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store content metadata",
            )

        # If file was uploaded, queue a task to process it
        if file_path:
            # Add to background tasks or Cloud Tasks
            task_data = {
                "content_id": content_id,
                "file_path": file_path,
                "file_name": file_name,
                "content_type": file.content_type if hasattr(file, "content_type") else None,
            }

            # Either use background tasks for local development
            background_tasks.add_task(task_service.process_file, task_data)

            # Or create a Cloud Task for production
            # task_service.create_file_processing_task(task_data)

        return {
            "id": content_id,
            "message": "Content uploaded successfully",
            "status": "processing" if file_path else "completed",
        }

    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload content: {str(e)}",
        )
