"""
API endpoints for bookmarks.
"""
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.repositories.bookmark_repository import BookmarkRepository
from app.repositories.content_repository import ContentRepository
from app.models.bookmark import BookmarkCreate
from app.models.content import Content
from app.utils.deps import get_current_user_hash

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bookmarks", tags=["Bookmarks"])


@router.post("/{content_id}")
async def add_bookmark(
    content_id: str,
    user_hash: str = Depends(get_current_user_hash)
) -> dict:
    """Add a bookmark for the current user."""
    # Verify content exists
    content_repo = ContentRepository()
    content = content_repo.get_by_id(content_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Content with ID {content_id} not found"
        )
    
    # Create bookmark
    bookmark_repo = BookmarkRepository()
    bookmark = BookmarkCreate(
        content_id=content_id,
        user_hash=user_hash
    )
    
    result = bookmark_repo.create(bookmark)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add bookmark"
        )
    
    return {"message": "Bookmark added successfully"}


@router.delete("/{content_id}")
async def remove_bookmark(
    content_id: str,
    user_hash: str = Depends(get_current_user_hash)
) -> dict:
    """Remove a bookmark for the current user."""
    # Remove bookmark
    bookmark_repo = BookmarkRepository()
    success = bookmark_repo.delete(user_hash, content_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove bookmark"
        )
    
    return {"message": "Bookmark removed successfully"}


@router.get("/")
async def get_bookmarks(
    user_hash: str = Depends(get_current_user_hash)
) -> List[Content]:
    """Get all bookmarks for the current user."""
    # Get bookmark content IDs
    bookmark_repo = BookmarkRepository()
    content_ids = bookmark_repo.get_by_user(user_hash)
    
    # Get content for each bookmark
    content_repo = ContentRepository()
    bookmarked_content = []
    
    for content_id in content_ids:
        content = content_repo.get_by_id(content_id)
        if content:
            bookmarked_content.append(content)
    
    return bookmarked_content


@router.get("/check/{content_id}")
async def check_bookmark(
    content_id: str,
    user_hash: str = Depends(get_current_user_hash)
) -> dict:
    """Check if content is bookmarked by current user."""
    bookmark_repo = BookmarkRepository()
    is_bookmarked = bookmark_repo.check_bookmark(user_hash, content_id)
    
    return {"is_bookmarked": is_bookmarked} 