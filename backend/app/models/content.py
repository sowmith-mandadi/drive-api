"""
Models for content management.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class Speaker(BaseModel):
    """Model for a presenter/speaker."""

    full_name: Optional[str] = Field(None, description="Speaker's full name")
    job_title: Optional[str] = Field(None, description="Speaker's job title")
    company: Optional[str] = Field(None, description="Speaker's company")
    type: Optional[str] = Field(
        None, description="Type of speaker: 'Googler', 'Partner', 'Customer', 'Community'"
    )
    industry: Optional[str] = Field(None, description="Speaker's industry")
    region: Optional[str] = Field(None, description="Speaker's region")


class ContentBase(BaseModel):
    """Base model for content."""

    title: str = Field(..., description="Title of the content", max_length=75)
    description: Optional[str] = Field(None, description="Description of the content")
    content_type: str = Field(..., description="Type of content")
    source: str = Field("upload", description="Source of content: 'upload', 'drive', 'external'")


class Session(BaseModel):
    """Full session model based on the complete schema."""

    # Core Identification & Status
    session_id: str = Field(..., description="Unique identifier for the session")
    status: str = Field(
        ..., description="Status: 'Scheduled', 'Published', 'Completed', 'Canceled'"
    )
    title: str = Field(..., description="Title of the session", max_length=75)
    abstract: str = Field(..., description="Abstract summary", max_length=550)
    demo_type: str = Field(
        ..., description="Type of demo: 'Keynote', 'Breakout', 'Workshop', 'Single Screen Demo'"
    )
    duration_minutes: Optional[str] = Field(None, description="Total run time in minutes")

    # Categorization details
    categorization: Dict[str, Any] = Field(
        default_factory=dict, description="Categorization details"
    )
    track: Optional[str] = Field(None, description="Primary category/track")
    learning_level: Optional[str] = Field(
        None, description="Learning level: 'Beginner', 'Intermediate', 'Advanced', 'All'"
    )
    topics: Optional[List[str]] = Field(None, description="Array of topic keywords")
    target_job_roles: Optional[List[str]] = Field(None, description="Array of target job roles")
    area_of_interest: Optional[List[str]] = Field(None, description="Array of broader interests")

    # Speakers/Presenters
    speakers: List[Speaker] = Field(default_factory=list, description="List of speakers")

    # Assets
    assets: Dict[str, Any] = Field(default_factory=dict, description="Asset details")
    presentation_slides_url: Optional[HttpUrl] = Field(
        None, description="URL to presentation slides"
    )
    recap_slides_url: Optional[HttpUrl] = Field(None, description="URL to recap slides")
    video_recording_status: Optional[str] = Field(
        None,
        description="Status of video recording: 'Available', 'Processing', 'Not Available', 'Pending'",
    )
    video_source_file_url: Optional[HttpUrl] = Field(None, description="URL to raw video file")
    video_youtube_url: Optional[HttpUrl] = Field(None, description="URL to YouTube video")

    # YouTube Publishing
    youtube_url: Optional[HttpUrl] = Field(None, description="YouTube URL")
    youtube_channel: Optional[str] = Field(None, description="YouTube channel")
    youtube_visibility: Optional[str] = Field(None, description="YouTube visibility setting")
    yt_video_title: Optional[str] = Field(None, description="YouTube video title")
    yt_description: Optional[str] = Field(None, description="YouTube video description")

    # System fields
    created_at: datetime = Field(
        default_factory=datetime.now, description="When the session was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now, description="When the session was last updated"
    )


class ContentCreate(BaseModel):
    """Model for creating content."""

    title: str = Field(..., description="Title of the content", max_length=75)
    description: Optional[str] = Field(None, description="Description of the content")
    content_type: str = Field(..., description="Type of content")
    source: str = Field("upload", description="Source of content: 'upload', 'drive', 'external'")
    tags: Optional[List[str]] = Field([], description="Tags associated with the content")
    metadata: Optional[Dict[str, Any]] = Field({}, description="Additional metadata")
    file_id: Optional[str] = Field(None, description="For Google Drive files")


class ContentUpdate(BaseModel):
    """Model for updating content."""

    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    used: Optional[bool] = None


class ContentInDB(ContentBase):
    """Model for content in database."""

    id: str
    session_id: Optional[str] = Field(None, description="Unique identifier for the session")
    status: Optional[str] = Field(
        None, description="Status: 'Scheduled', 'Published', 'Completed', 'Canceled'"
    )
    created_at: datetime
    updated_at: datetime

    # File and storage related fields
    file_path: Optional[str] = None
    drive_id: Optional[str] = None
    drive_link: Optional[str] = None

    # Basic content metadata
    abstract: Optional[str] = Field(None, description="Abstract summary", max_length=550)
    demo_type: Optional[str] = Field(
        None, description="Type of demo: 'Keynote', 'Breakout', 'Workshop', 'Single Screen Demo'"
    )
    duration_minutes: Optional[str] = None
    tags: List[str] = []
    metadata: Dict[str, Any] = {}
    extracted_text: Optional[str] = None
    page_content: Optional[Dict[str, str]] = None  # Map of page/slide numbers to content
    used: bool = False
    embedding_id: Optional[str] = None
    ai_tags: Optional[List[str]] = None

    # Categorization
    categorization: Dict[str, Any] = Field(
        default_factory=dict, description="Categorization details"
    )
    track: Optional[str] = None
    learning_level: Optional[str] = None  # "Beginner", "Intermediate", "Advanced", "All"
    topics: Optional[List[str]] = None
    target_job_roles: Optional[List[str]] = None
    area_of_interest: Optional[List[str]] = None

    # Presenter information
    speakers: List[Speaker] = Field(default_factory=list, description="List of speakers/presenters")

    # Assets
    assets: Dict[str, Any] = Field(default_factory=dict, description="Asset details")
    presentation_slides_url: Optional[HttpUrl] = None
    recap_slides_url: Optional[HttpUrl] = None
    video_recording_status: Optional[
        str
    ] = None  # "Available", "Processing", "Not Available", "Pending"
    video_source_file_url: Optional[HttpUrl] = None
    video_youtube_url: Optional[HttpUrl] = None

    # YouTube publishing info
    youtube_url: Optional[HttpUrl] = None
    youtube_channel: Optional[str] = None
    youtube_visibility: Optional[str] = None
    yt_video_title: Optional[str] = None
    yt_description: Optional[str] = None


class Content(ContentInDB):
    """Model for content response."""

    class Config:
        """Pydantic config."""

        from_attributes = True


class DriveFile(BaseModel):
    """Model for Google Drive file."""

    id: str
    name: str
    mimeType: str
    webViewLink: Optional[str] = None
    thumbnailLink: Optional[str] = None
    iconLink: Optional[str] = None
    size: Optional[int] = None


class DriveImportRequest(BaseModel):
    """Model for Drive import request."""

    fileIds: List[str]
    metadata: Optional[Dict[str, Any]] = {}
