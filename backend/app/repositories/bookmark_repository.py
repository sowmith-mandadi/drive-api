"""
Repository for bookmark operations.
"""
import logging
from datetime import datetime
from typing import List, Optional

from app.db.firestore_client import FirestoreClient
from app.models.bookmark import BookmarkCreate, BookmarkInDB

# Setup logging
logger = logging.getLogger(__name__)

# Collection name
COLLECTION = "bookmarks"


class BookmarkRepository:
    """Repository for bookmark operations."""

    def __init__(self):
        """Initialize the repository."""
        self.db = FirestoreClient()

    def create(self, bookmark: BookmarkCreate) -> Optional[BookmarkInDB]:
        """Create a new bookmark."""
        # Check if bookmark already exists
        existing = self.get_by_user_and_content(bookmark.user_hash, bookmark.content_id)
        if existing:
            return existing
            
        # Create new bookmark
        bookmark_id = self.db.generate_id()
        now = datetime.now()
        
        bookmark_data = bookmark.dict()
        bookmark_data.update({
            "created_at": now
        })
        
        success = self.db.create_document(COLLECTION, bookmark_id, bookmark_data)
        if not success:
            return None
            
        bookmark_data["id"] = bookmark_id
        return BookmarkInDB(**bookmark_data)

    def delete(self, user_hash: str, content_id: str) -> bool:
        """Delete a bookmark."""
        # Find the bookmark
        bookmark = self.get_by_user_and_content(user_hash, content_id)
        if not bookmark:
            return True  # Already doesn't exist
            
        # Delete the bookmark
        return self.db.delete_document(COLLECTION, bookmark.id)

    def get_by_user_and_content(self, user_hash: str, content_id: str) -> Optional[BookmarkInDB]:
        """Get a bookmark by user hash and content ID."""
        filters = [
            ("user_hash", "==", user_hash),
            ("content_id", "==", content_id)
        ]
        
        results = self.db.list_documents(COLLECTION, limit=1, filters=filters)
        if not results:
            return None
            
        return BookmarkInDB(**results[0])

    def get_by_user(self, user_hash: str) -> List[str]:
        """Get all bookmarks for a user hash."""
        filters = [("user_hash", "==", user_hash)]
        
        results = self.db.list_documents(COLLECTION, limit=100, filters=filters)
        return [doc["content_id"] for doc in results]

    def check_bookmark(self, user_hash: str, content_id: str) -> bool:
        """Check if content is bookmarked by user."""
        return self.get_by_user_and_content(user_hash, content_id) is not None 