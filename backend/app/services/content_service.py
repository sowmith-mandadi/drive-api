"""
Content management service for the FastAPI application.
"""
import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.models.content import ContentCreate, ContentInDB, ContentUpdate
from app.repositories.content_repository import ContentRepository

# Setup logging
logger = logging.getLogger(__name__)


class ContentService:
    """Service for content management."""

    def __init__(self) -> None:
        """Initialize the content service."""
        self.repository = ContentRepository()

        # Use environment variable for upload directory with fallback to /tmp path
        # This ensures App Engine compatibility
        self.upload_dir = settings.UPLOAD_DIR

        # Log the upload directory being used
        logger.info(f"ContentService using upload directory: {self.upload_dir}")

        # In App Engine, force to use /tmp directory if the original path is not writable
        if not os.path.exists(self.upload_dir) or not os.access(self.upload_dir, os.W_OK):
            app_engine_tmp = "/tmp/uploads"
            logger.warning(
                f"Upload directory {self.upload_dir} not writable or doesn't exist. "
                f"Falling back to App Engine safe path: {app_engine_tmp}"
            )
            self.upload_dir = app_engine_tmp

        # Create directory if it doesn't exist
        try:
            os.makedirs(self.upload_dir, exist_ok=True)

            # Verify the directory exists and is writable
            if not os.path.exists(self.upload_dir):
                logger.error(f"Failed to create upload directory: {self.upload_dir}")
            elif not os.access(self.upload_dir, os.W_OK):
                logger.error(f"Upload directory is not writable: {self.upload_dir}")
            else:
                logger.info(f"Successfully initialized upload directory: {self.upload_dir}")

        except Exception as e:
            logger.error(f"Error setting up upload directory: {str(e)}", exc_info=True)
            # Fall back to using memory for uploads if we can't use the filesystem
            logger.warning("Using in-memory processing due to filesystem issues")

    def get_all_content(self, limit: int = 100, offset: int = 0) -> List[ContentInDB]:
        """Get all content items with pagination.

        Args:
            limit: Maximum number of items to return.
            offset: Number of items to skip.

        Returns:
            List of content items.
        """
        return self.repository.get_all(limit=limit, offset=offset)

    def get_content_by_id(self, content_id: str) -> Optional[ContentInDB]:
        """Get content by ID.

        Args:
            content_id: ID of the content.

        Returns:
            Content item or None if not found.
        """
        return self.repository.get_by_id(content_id)

    def create_content(self, content_data: ContentCreate) -> ContentInDB:
        """Create a new content item.

        Args:
            content_data: Content creation data.

        Returns:
            Created content item.
        """
        content_id = str(uuid.uuid4())
        content = self.repository.create(content_data, content_id)

        if not content:
            # If repository creation failed, fall back to returning a local object
            # This ensures API compatibility but won't persist
            logger.warning("Failed to create content in repository, using local object")
            now = datetime.now()
            content = ContentInDB(
                id=content_id,
                title=content_data.title,
                description=content_data.description,
                contentType=content_data.contentType,
                source=content_data.source,
                tags=content_data.tags or [],
                metadata=content_data.metadata or {},
                createdAt=now,
                updatedAt=now,
                driveId=content_data.fileId if content_data.source == "drive" else None,
            )

        logger.info(f"Created content item with ID {content_id}")
        return content

    def update_content(self, content_id: str, update_data: ContentUpdate) -> Optional[ContentInDB]:
        """Update an existing content item.

        Args:
            content_id: ID of the content to update.
            update_data: Content update data.

        Returns:
            Updated content item or None if not found.
        """
        updated_content = self.repository.update(content_id, update_data)
        if updated_content:
            logger.info(f"Updated content item with ID {content_id}")

        return updated_content

    def update_content_fields(
        self, content_id: str, fields: Dict[str, Any]
    ) -> Optional[ContentInDB]:
        """Update specific fields of existing content.

        This method is more flexible than update_content as it can update any field,
        not just those defined in ContentUpdate.

        Args:
            content_id: ID of the content to update.
            fields: Dictionary of fields to update.

        Returns:
            Updated content item or None if not found.
        """
        try:
            # Check if content exists
            content = self.repository.get_by_id(content_id)
            if not content:
                return None

            # Map any camelCase fields to snake_case for Firestore storage
            mapped_fields = {}
            for key, value in fields.items():
                # Convert camelCase to snake_case if needed
                if key in [
                    "contentType", "sessionId", "createdAt", "updatedAt", 
                    "filePath", "driveId", "driveLink", "demoType", 
                    "durationMinutes", "extractedText", "pageContent", 
                    "embeddingId", "aiTags", "learningLevel", "targetJobRoles", 
                    "areasOfInterest", "presentationSlidesUrl", "recapSlidesUrl", 
                    "sessionRecordingStatus", "videoSourceFileUrl", "videoYoutubeUrl", 
                    "youtubeUrl", "youtubeChannel", "youtubeVisibility", 
                    "ytVideoTitle", "ytDescription"
                ]:
                    # Convert camelCase to snake_case
                    snake_key = ''.join(['_' + c.lower() if c.isupper() else c for c in key])
                    snake_key = snake_key.lstrip('_')
                    mapped_fields[snake_key] = value
                else:
                    # Keep original key if not in the mapping list
                    mapped_fields[key] = value

            # Add updated timestamp
            mapped_fields["updated_at"] = datetime.now().isoformat()

            # Update in repository
            success = self.repository.firestore.update_document(
                self.repository.collection, content_id, mapped_fields
            )

            if not success:
                return None

            # Get updated content
            return self.repository.get_by_id(content_id)
        except Exception as e:
            logger.error(f"Error updating content fields: {str(e)}")
            return None

    def delete_content(self, content_id: str) -> bool:
        """Delete a content item.

        Args:
            content_id: ID of the content to delete.

        Returns:
            True if deleted, False if not found.
        """
        # Get content to check for file path
        content = self.get_content_by_id(content_id)
        if not content:
            return False

        # Delete from repository
        success = self.repository.delete(content_id)
        if not success:
            return False

        # Clean up file if exists
        file_path = content.filePath  # Use camelCase field name
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Deleted file at {file_path}")
            except Exception as e:
                logger.error(f"Failed to delete file at {file_path}: {str(e)}")

        logger.info(f"Deleted content item with ID {content_id}")
        return True

    def search_content(
        self, query: str, filters: Optional[Dict[str, Any]] = None
    ) -> List[ContentInDB]:
        """Search for content based on query and filters.

        Args:
            query: Search query.
            filters: Additional filters.

        Returns:
            List of matching content items.
        """
        return self.repository.search(query, filters)

    def update_content_file(
        self,
        content_id: str,
        file_path: str,
        extracted_text: Optional[str] = None,
        page_content: Optional[Dict[str, str]] = None,
    ) -> bool:
        """Update content with file information.

        Args:
            content_id: ID of the content.
            file_path: Path to the file.
            extracted_text: Optional extracted text.
            page_content: Optional page/slide content.

        Returns:
            True if successful, False otherwise.
        """
        # Update file path
        success = self.repository.update_file_path(content_id, file_path)
        if not success:
            return False

        # Update extracted text if provided
        if extracted_text and page_content:
            success = self.repository.update_extracted_text(
                content_id, extracted_text, page_content
            )
            if not success:
                return False

        return True

    def get_popular_tags(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get the most popular tags.

        Args:
            limit: Maximum number of tags to return.

        Returns:
            List of tag objects with counts.
        """
        # Get all content to analyze tags
        all_content = self.repository.get_all(limit=500)  # Limit to reasonable number for analysis

        # Count tags
        tag_counts: Dict[str, int] = {}
        for content in all_content:
            for tag in content.tags:
                if tag in tag_counts:
                    tag_counts[tag] += 1
                else:
                    tag_counts[tag] = 1

        # Sort by count (descending)
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)

        # Format results
        result = [{"tag": tag, "count": count} for tag, count in sorted_tags[:limit]]

        return result

    def get_recent_content(self, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """Get recent content with pagination.

        Args:
            page: Page number (1-indexed).
            page_size: Number of items per page.

        Returns:
            Dictionary with content items and pagination info.
        """
        # Calculate offset
        offset = (page - 1) * page_size

        # Get content with pagination
        content_items = self.repository.get_all(limit=page_size, offset=offset)

        # Sort by createdAt (most recent first)
        content_items.sort(key=lambda x: x.createdAt, reverse=True)

        # Get total count (for pagination)
        total_count = len(self.repository.get_all())  # This is inefficient but works for now

        # Calculate pagination info
        total_pages = (total_count + page_size - 1) // page_size

        # Format result
        result = {
            "items": content_items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": total_count,
                "total_pages": total_pages,
            },
        }

        return result
