"""
Models for content management.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class Speaker(BaseModel):
    """Model for a presenter/speaker."""

    fullName: Optional[str] = Field(None, description="Speaker's full name")
    jobTitle: Optional[str] = Field(None, description="Speaker's job title")
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
    contentType: str = Field(..., description="Type of content")
    source: str = Field("upload", description="Source of content: 'upload', 'drive', 'external'")


class Session(BaseModel):
    """Full session model based on the complete schema."""

    # Core Identification & Status
    sessionId: str = Field(..., description="Unique identifier for the session")
    status: str = Field(
        ..., description="Status: 'Scheduled', 'Published', 'Completed', 'Canceled'"
    )
    title: str = Field(..., description="Title of the session", max_length=75)
    abstract: str = Field(..., description="Abstract summary", max_length=550)
    demoType: str = Field(
        ..., description="Type of demo: 'Keynote', 'Breakout', 'Workshop', 'Single Screen Demo'"
    )
    durationMinutes: Optional[str] = Field(None, description="Total run time in minutes")

    # Categorization details
    categorization: Dict[str, Any] = Field(
        default_factory=dict, description="Categorization details"
    )
    track: Optional[str] = Field(None, description="Primary category/track")
    learningLevel: Optional[str] = Field(
        None, description="Learning level: 'Beginner', 'Intermediate', 'Advanced', 'All'"
    )
    topics: Optional[List[str]] = Field(None, description="Array of topic keywords")
    targetJobRoles: Optional[List[str]] = Field(None, description="Array of target job roles")
    areasOfInterest: Optional[List[str]] = Field(None, description="Array of areas of interest")

    # Speakers/Presenters
    speakers: List[Speaker] = Field(default_factory=list, description="List of speakers")

    # Assets
    assets: Dict[str, Any] = Field(default_factory=dict, description="Asset details")
    presentationSlidesUrl: Optional[HttpUrl] = Field(
        None, description="URL to presentation slides"
    )
    recapSlidesUrl: Optional[HttpUrl] = Field(None, description="URL to recap slides")
    videoRecordingStatus: Optional[str] = Field(
        None,
        description="Status of video recording: 'Available', 'Processing', 'Not Available', 'Pending'",
    )
    videoSourceFileUrl: Optional[HttpUrl] = Field(None, description="URL to raw video file")
    videoYoutubeUrl: Optional[HttpUrl] = Field(None, description="URL to YouTube video")

    # YouTube Publishing
    youtubeUrl: Optional[HttpUrl] = Field(None, description="YouTube URL")
    youtubeChannel: Optional[str] = Field(None, description="YouTube channel")
    youtubeVisibility: Optional[str] = Field(None, description="YouTube visibility setting")
    ytVideoTitle: Optional[str] = Field(None, description="YouTube video title")
    ytDescription: Optional[str] = Field(None, description="YouTube video description")

    # System fields
    createdAt: datetime = Field(
        default_factory=datetime.now, description="When the session was created"
    )
    updatedAt: datetime = Field(
        default_factory=datetime.now, description="When the session was last updated"
    )


class ContentCreate(BaseModel):
    """Model for creating content."""

    title: str = Field(..., description="Title of the content", max_length=75)
    description: Optional[str] = Field(None, description="Description of the content")
    contentType: str = Field(..., description="Type of content")
    source: str = Field("upload", description="Source of content: 'upload', 'drive', 'external'")
    tags: Optional[List[str]] = Field([], description="Tags associated with the content")
    metadata: Optional[Dict[str, Any]] = Field({}, description="Additional metadata")
    fileId: Optional[str] = Field(None, description="For Google Drive files")


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
    sessionId: Optional[str] = Field(None, description="Unique identifier for the session")
    status: Optional[str] = Field(
        None, description="Status: 'Scheduled', 'Published', 'Completed', 'Canceled'"
    )
    createdAt: datetime
    updatedAt: datetime

    # File and storage related fields
    filePath: Optional[str] = None
    driveId: Optional[str] = None
    driveLink: Optional[str] = None

    # Basic content metadata
    abstract: Optional[str] = Field(None, description="Abstract summary", max_length=550)
    demoType: Optional[str] = Field(
        None, description="Type of demo: 'Keynote', 'Breakout', 'Workshop', 'Single Screen Demo'"
    )
    durationMinutes: Optional[str] = None
    tags: List[str] = []
    metadata: Dict[str, Any] = {}
    extractedText: Optional[str] = None
    pageContent: Optional[Dict[str, str]] = None  # Map of page/slide numbers to content
    used: bool = False
    embeddingId: Optional[str] = None
    aiTags: Optional[List[str]] = None

    # Categorization
    categorization: Dict[str, Any] = Field(
        default_factory=dict, description="Categorization details"
    )
    track: Optional[str] = None
    learningLevel: Optional[str] = None  # "Beginner", "Intermediate", "Advanced", "All"
    topics: Optional[List[str]] = None
    targetJobRoles: Optional[List[str]] = None
    areasOfInterest: Optional[List[str]] = None

    # Presenter information
    speakers: List[Speaker] = Field(default_factory=list, description="List of speakers/presenters")

    # Assets
    assets: Dict[str, Any] = Field(default_factory=dict, description="Asset details")
    presentationSlidesUrl: Optional[HttpUrl] = None
    recapSlidesUrl: Optional[HttpUrl] = None
    videoRecordingStatus: Optional[
        str
    ] = None  # "Available", "Processing", "Not Available", "Pending"
    videoSourceFileUrl: Optional[HttpUrl] = None
    videoYoutubeUrl: Optional[HttpUrl] = None

    # YouTube publishing info
    youtubeUrl: Optional[HttpUrl] = None
    youtubeChannel: Optional[str] = None
    youtubeVisibility: Optional[str] = None
    ytVideoTitle: Optional[str] = None
    ytDescription: Optional[str] = None


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
