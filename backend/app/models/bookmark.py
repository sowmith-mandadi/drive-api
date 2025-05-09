"""
Model for anonymous user bookmarks.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field


class BookmarkCreate(BaseModel):
    """Model for creating a bookmark."""
    content_id: str
    user_hash: str  # Anonymized user identifier


class BookmarkInDB(BookmarkCreate):
    """Model for bookmark in database."""
    id: str
    created_at: datetime 