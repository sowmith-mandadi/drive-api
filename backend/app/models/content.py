"""
Models for content management.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ContentBase(BaseModel):
    """Base model for content."""
    title: str
    description: Optional[str] = None
    content_type: str
    source: str = "upload"  # "upload", "drive", "external"


class ContentCreate(ContentBase):
    """Model for creating content."""
    tags: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = {}
    file_id: Optional[str] = None  # For Google Drive files


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
    created_at: datetime
    updated_at: datetime
    file_path: Optional[str] = None
    drive_id: Optional[str] = None
    drive_link: Optional[str] = None
    tags: List[str] = []
    metadata: Dict[str, Any] = {}
    extracted_text: Optional[str] = None
    page_content: Optional[Dict[str, str]] = None  # Map of page/slide numbers to content
    used: bool = False
    embedding_id: Optional[str] = None


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