"""
Pydantic schemas for Google Drive functionality.
"""
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class DriveCredentials(BaseModel):
    """Schema for Google Drive API credentials."""

    token: str = Field(..., description="OAuth token for Google API")
    refresh_token: Optional[str] = Field(None, description="Refresh token for Google API")
    token_uri: str = Field(..., description="Token URI for Google API")
    client_id: str = Field(..., description="Client ID for Google API")
    client_secret: str = Field(..., description="Client secret for Google API")
    scopes: List[str] = Field(..., description="OAuth scopes for Google API")
    expiry: Optional[datetime] = Field(None, description="Token expiry timestamp")


class DriveFolder(BaseModel):
    """Schema for Google Drive folder information."""

    id: str = Field(..., description="Google Drive folder ID")
    name: str = Field(..., description="Google Drive folder name")
    mimeType: str = Field(
        "application/vnd.google-apps.folder", description="MIME type for Google Drive folder"
    )
    createdTime: Optional[datetime] = Field(None, description="Folder creation timestamp")
    parents: Optional[List[str]] = Field(None, description="IDs of parent folders")


class DriveFile(BaseModel):
    """Schema for Google Drive file information."""

    id: str = Field(..., description="Google Drive file ID")
    name: str = Field(..., description="Google Drive file name")
    mimeType: str = Field(..., description="MIME type of the file")
    size: Optional[int] = Field(None, description="File size in bytes")
    webViewLink: Optional[HttpUrl] = Field(None, description="URL to view the file in browser")
    thumbnailLink: Optional[HttpUrl] = Field(None, description="URL to thumbnail image")
    createdTime: Optional[datetime] = Field(None, description="File creation timestamp")
    modifiedTime: Optional[datetime] = Field(None, description="Last modification timestamp")
    parents: Optional[List[str]] = Field(None, description="IDs of parent folders")


class DriveImportRequest(BaseModel):
    """Schema for requesting to import files from Google Drive."""

    file_ids: List[str] = Field(..., description="List of Google Drive file IDs to import")
    category: Optional[str] = Field(None, description="Content category")

    class Config:
        schema_extra = {
            "example": {
                "file_ids": ["1A2B3C4D5E6F7G8H9I0J", "1B2C3D4E5F6G7H8I9J0K"],
                "category": "Presentations",
            }
        }


class DriveImportResponse(BaseModel):
    """Schema for response after importing from Google Drive."""

    success: bool = Field(..., description="Whether the import was successful")
    imported_count: int = Field(..., description="Number of successfully imported files")
    failed_count: int = Field(..., description="Number of files that failed to import")
    content_ids: Optional[List[str]] = Field(None, description="IDs of created content items")
    error_details: Optional[Dict[str, str]] = Field(None, description="Details of any errors")
