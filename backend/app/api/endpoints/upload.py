"""
API endpoints for file uploads.
"""
import json
import os
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, Field, HttpUrl

from app.core.logging import configure_logging
from app.db.firestore_client import FirestoreClient
from app.models.content import Content, ContentCreate, Speaker
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
    company: Optional[str] = None
    title: Optional[str] = None
    industry: Optional[str] = None


class Comment(BaseModel):
    """Model for comments."""

    id: Optional[str] = None
    author: str
    text: str
    dateCreated: Optional[datetime] = None


class ContentUpload(BaseModel):
    """Model for content upload metadata."""

    # Core fields
    title: str = Field(..., description="Title of the content", max_length=75)
    description: str = Field("", description="Description of the content")
    abstract: Optional[str] = Field(None, description="Abstract summary", max_length=550)
    sessionId: Optional[str] = Field(None, description="Unique session identifier")
    status: Optional[str] = Field(
        None, description="Status: 'Scheduled', 'Published', 'Completed', 'Canceled'"
    )

    # Categorization
    track: str = Field(..., description="Primary category/track")
    tags: List[str] = Field([], description="Tags associated with the content")
    sessionType: str = Field(..., description="Type of session")
    demoType: Optional[str] = Field(
        None, description="Type of demo: 'Keynote', 'Breakout', 'Workshop', 'Single Screen Demo'"
    )
    sessionDate: Optional[str] = Field(None, description="Date of the session")
    durationMinutes: Optional[str] = Field(None, description="Total run time in minutes")
    learningLevel: Optional[str] = Field(
        None, description="Learning level: 'Beginner', 'Intermediate', 'Advanced', 'All'"
    )
    topic: Optional[str] = Field(None, description="Main topic")
    topics: Optional[List[str]] = Field(None, description="Array of topic keywords")
    jobRole: Optional[str] = Field(None, description="Job role")
    targetJobRoles: Optional[List[str]] = Field(None, description="Array of target job roles")
    areasOfInterest: Optional[List[str]] = Field(None, description="Array of areas of interest")
    industry: Optional[str] = Field(None, description="Industry")

    # Presenters
    presenters: List[Presenter] = Field([], description="List of presenters")

    # Assets
    presentationSlidesUrl: Optional[HttpUrl] = Field(None, description="URL to presentation slides")
    recapSlidesUrl: Optional[HttpUrl] = Field(None, description="URL to recap slides")
    videoRecordingStatus: Optional[str] = Field(None, description="Status of video recording")
    videoSourceFileUrl: Optional[HttpUrl] = Field(None, description="URL to raw video file")
    videoYoutubeUrl: Optional[HttpUrl] = Field(None, description="URL to YouTube video")

    # YouTube Publishing
    youtubeUrl: Optional[HttpUrl] = Field(None, description="YouTube URL")
    ytVideoTitle: Optional[str] = Field(None, description="YouTube video title")

    # Other
    used: Optional[bool] = Field(False, description="Whether the content has been used")
    aiTags: Optional[List[str]] = Field(None, description="AI-generated tags")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_content(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    description: str = Form(""),
    abstract: Optional[str] = Form(None),
    sessionId: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
    track: str = Form(...),
    tags: str = Form("[]"),  # JSON string of tags
    sessionType: str = Form(...),
    demoType: Optional[str] = Form(None),
    sessionDate: Optional[str] = Form(None),
    durationMinutes: Optional[str] = Form(None),
    learningLevel: Optional[str] = Form(None),
    topic: Optional[str] = Form(None),
    topics: Optional[str] = Form(None),  # JSON string of topics
    jobRole: Optional[str] = Form(None),
    targetJobRoles: Optional[str] = Form(None),  # JSON string of job roles
    areasOfInterest: Optional[str] = Form(None),  # JSON string of areas
    industry: Optional[str] = Form(None),
    presenters: str = Form("[]"),  # JSON string of presenters
    # Asset URLs
    presentationSlidesUrl: Optional[str] = Form(None),
    recapSlidesUrl: Optional[str] = Form(None),
    videoRecordingStatus: Optional[str] = Form(None),
    driveLink: Optional[str] = Form(None),
    videoYoutubeUrl: Optional[str] = Form(None),
    ytVideoTitle: Optional[str] = Form(None),
    ytDescription: Optional[str] = Form(None),
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
        topics_list = json.loads(topics) if topics else []
        target_job_roles_list = json.loads(targetJobRoles) if targetJobRoles else []
        areas_of_interest_list = json.loads(areasOfInterest) if areasOfInterest else []

        # Generate a new ID
        content_id = firestore.generate_id()

        # Use the temp directory from environment variable or default to /tmp which is writable in App Engine
        temp_dir = os.environ.get("TEMP_UPLOAD_DIR", "/tmp/uploads")
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

        # Add all URLs directly to fileUrls
        fileUrls = []
        
        # Handle presentation slides URL
        if presentationSlidesUrl:
            fileUrls.append({
                "contentType": "presentation",
                "presentation_type": "presentation_slides",
                "name": "Presentation Slides",
                "source": "drive",
                "drive_url": presentationSlidesUrl,
                "driveId": presentationSlidesUrl.split("/d/")[1].split("/")[0] if "/d/" in presentationSlidesUrl else "",
                "gcs_path": None,
                "type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                "size": 0,
                "thumbnailLink": None,
                "url": None
            })
        
        # Handle recap slides URL
        if recapSlidesUrl:
            fileUrls.append({
                "contentType": "presentation",
                "presentation_type": "recap_slides",
                "name": "Recap Slides",
                "source": "drive",
                "drive_url": recapSlidesUrl,
                "driveId": recapSlidesUrl.split("/d/")[1].split("/")[0] if "/d/" in recapSlidesUrl else "",
                "gcs_path": None,
                "type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                "size": 0,
                "thumbnailLink": None,
                "url": None
            })
        
        # Handle drive link
        if driveLink:
            fileUrls.append({
                "contentType": "folder",
                "presentation_type": "drive_folder",
                "name": "Drive Folder",
                "source": "drive",
                "drive_url": driveLink,
                "gcs_path": None
            })
        
        # Handle YouTube URL
        if videoYoutubeUrl:
            fileUrls.append({
                "contentType": "video",
                "presentation_type": "youtube_video",
                "name": "YouTube Video",
                "source": "youtube",
                "drive_url": videoYoutubeUrl,
                "gcs_path": None
            })

        # Create content data
        now = datetime.now()
        content_data = {
            "id": content_id,
            "title": title,
            "description": description,
            "abstract": abstract,
            "sessionId": sessionId,
            "status": status,
            "track": track,
            "tags": tags_list,
            "sessionType": sessionType,
            "demoType": demoType,
            "sessionDate": sessionDate,
            "durationMinutes": durationMinutes,
            "learningLevel": learningLevel,
            "topic": topic,
            "topics": topics_list,
            "jobRole": jobRole,
            "targetJobRoles": target_job_roles_list,
            "areasOfInterest": areas_of_interest_list,
            "industry": industry,
            "presenters": presenters_list,
            "dateCreated": now.isoformat(),
            "dateModified": now.isoformat(),
            "fileUrls": fileUrls,
            "used": False,
            # Asset URLs - keep for backward compatibility
            "presentationSlidesUrl": presentationSlidesUrl,
            "recapSlidesUrl": recapSlidesUrl,
            "videoRecordingStatus": videoRecordingStatus,
            "driveLink": driveLink,
            "videoYoutubeUrl": videoYoutubeUrl,
            "ytVideoTitle": ytVideoTitle,
            "ytDescription": ytDescription,
            # Include a metadata field with all root level metadata
            "metadata": {
                "abstract": abstract,
                "sessionId": sessionId,
                "status": status,
                "track": track,
                "sessionType": sessionType,
                "demoType": demoType,
                "sessionDate": sessionDate,
                "durationMinutes": durationMinutes,
                "learningLevel": learningLevel,
                "topic": topic,
                "topics": topics_list,
                "jobRole": jobRole,
                "targetJobRoles": target_job_roles_list,
                "areasOfInterest": areas_of_interest_list,
                "industry": industry,
                "presentationSlidesUrl": presentationSlidesUrl,
                "recapSlidesUrl": recapSlidesUrl,
                "videoRecordingStatus": videoRecordingStatus,
                "videoYoutubeUrl": videoYoutubeUrl,
                "ytVideoTitle": ytVideoTitle,
                "ytDescription": ytDescription
            }
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
                "contentId": content_id,
                "filePath": file_path,
                "fileName": file_name,
                "contentType": file.content_type if hasattr(file, "content_type") else None,
            }

            # Either use background tasks for local development
            background_tasks.add_task(task_service.process_file, task_data)

            # Or create a Cloud Task for production
            # task_service.create_file_processing_task(task_data)
        
        # Ensure we only have the 4 required types in fileUrls
        content_data["fileUrls"] = [
            entry for entry in content_data["fileUrls"]
            if entry.get("presentation_type") in ["presentation_slides", "recap_slides", "drive_folder", "youtube_video"]
        ]
        
        # Remove any iconLink fields and ensure webViewLink is converted to drive_url
        for entry in content_data["fileUrls"]:
            if "iconLink" in entry:
                del entry["iconLink"]
            if "webViewLink" in entry:
                entry["drive_url"] = entry["webViewLink"]
                del entry["webViewLink"]

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
