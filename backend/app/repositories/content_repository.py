"""
Content repository for database operations.
"""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.db.firestore_client import FirestoreClient
from app.models.content import ContentCreate, ContentInDB, ContentUpdate

# Setup logging
logger = logging.getLogger(__name__)


class ContentRepository:
    """Repository for content-related database operations."""

    def __init__(self):
        """Initialize the content repository."""
        self.firestore = FirestoreClient()
        self.collection = settings.FIRESTORE_COLLECTION_CONTENT

    def get_all(self, limit: int = 100, offset: int = 0) -> List[ContentInDB]:
        """Get all content items with pagination.

        Args:
            limit: Maximum number of items to return.
            offset: Number of items to skip.

        Returns:
            List of content items.
        """
        # Get documents from Firestore
        docs = self.firestore.list_documents(
            self.collection, limit=limit, offset=offset, order_by="created_at"
        )

        # Convert to ContentInDB models
        return [self._to_content_model(doc) for doc in docs]

    def get_by_id(self, content_id: str) -> Optional[ContentInDB]:
        """Get content by ID.

        Args:
            content_id: ID of the content.

        Returns:
            Content item or None if not found.
        """
        doc = self.firestore.get_document(self.collection, content_id)
        if not doc:
            return None

        return self._to_content_model(doc)

    def create(
        self, content_data: ContentCreate, content_id: Optional[str] = None
    ) -> Optional[ContentInDB]:
        """Create a new content item.

        Args:
            content_data: Content creation data.
            content_id: Optional ID for the content (will be generated if not provided).

        Returns:
            Created content item or None if failed.
        """
        try:
            # Prepare data
            now = datetime.now().isoformat()

            # Create content object
            content_dict = {
                "title": content_data.title,
                "description": content_data.description,
                "content_type": content_data.content_type,
                "source": content_data.source,
                "tags": content_data.tags or [],
                "metadata": content_data.metadata or {},
                "created_at": now,
                "updated_at": now,
                "used": False,
            }

            # Add Drive ID if available
            if content_data.source == "drive" and content_data.file_id:
                content_dict["drive_id"] = content_data.file_id

            # Create in Firestore
            success = self.firestore.create_document(
                self.collection,
                content_id or "",  # Ensure we pass a string
                content_dict
            )

            if not success:
                return None

            # Get the created content
            if content_id:
                created_content = self.get_by_id(content_id)
                return created_content
            return None
        except Exception as e:
            logger.error(f"Error creating content: {str(e)}")
            return None

    def update(self, content_id: str, update_data: ContentUpdate) -> Optional[ContentInDB]:
        """Update an existing content item.

        Args:
            content_id: ID of the content to update.
            update_data: Content update data.

        Returns:
            Updated content item or None if not found or failed.
        """
        try:
            # Check if content exists
            existing_content = self.get_by_id(content_id)
            if not existing_content:
                return None

            # Prepare update data
            update_dict = {}

            if update_data.title is not None:
                update_dict["title"] = update_data.title
            if update_data.description is not None:
                update_dict["description"] = update_data.description
            if update_data.tags is not None:
                update_dict["tags"] = update_data.tags
            if update_data.metadata is not None:
                update_dict["metadata"] = update_data.metadata
            if update_data.used is not None:
                update_dict["used"] = update_data.used

            # Add updated timestamp
            update_dict["updated_at"] = datetime.now().isoformat()

            # Update in Firestore
            success = self.firestore.update_document(self.collection, content_id, update_dict)

            if not success:
                return None

            # Get the updated content
            updated_content = self.get_by_id(content_id)
            return updated_content
        except Exception as e:
            logger.error(f"Error updating content: {str(e)}")
            return None

    def delete(self, content_id: str) -> bool:
        """Delete a content item.

        Args:
            content_id: ID of the content to delete.

        Returns:
            True if deleted, False if not found or failed.
        """
        return self.firestore.delete_document(self.collection, content_id)

    def search(
        self, query: Optional[str] = None, filters: Optional[Dict[str, Any]] = None
    ) -> List[ContentInDB]:
        """Search for content based on query and filters.

        Args:
            query: Search query.
            filters: Additional filters.

        Returns:
            List of matching content items.
        """
        try:
            # Prepare Firestore filters
            firestore_filters = []

            if filters:
                for key, value in filters.items():
                    # Handle special case for metadata fields
                    if key.startswith("metadata."):
                        metadata_key = key.split(".", 1)[1]
                        # Note: This is a simplification.
                        # Firestore requires using complex queries for nested fields
                        continue

                    # Handle special case for tags
                    elif key == "tags":
                        # This is also a simplification. In production, you would need
                        # to use array-contains or array-contains-any depending on the use case
                        continue

                    # Handle normal fields
                    else:
                        firestore_filters.append((key, "==", value))

            # Search fields
            search_fields = ["title", "description", "extracted_text", "tags"]

            # Get matching documents
            docs = self.firestore.search_documents(
                self.collection, query or "", search_fields, filters=firestore_filters
            )

            # Convert to ContentInDB models
            contents = [self._to_content_model(doc) for doc in docs]

            # Apply additional filtering for metadata and tags
            # (since we couldn't do it efficiently in Firestore)
            if filters:
                filtered_contents = []

                for content in contents:
                    include = True

                    for key, value in filters.items():
                        # Handle metadata fields
                        if key.startswith("metadata."):
                            metadata_key = key.split(".", 1)[1]
                            if (
                                metadata_key not in content.metadata
                                or content.metadata[metadata_key] != value
                            ):
                                include = False
                                break

                        # Handle tags
                        elif key == "tags":
                            if not all(tag in content.tags for tag in value):
                                include = False
                                break

                    if include:
                        filtered_contents.append(content)

                return filtered_contents

            return contents
        except Exception as e:
            logger.error(f"Error searching content: {str(e)}")
            return []

    def update_extracted_text(
        self, content_id: str, extracted_text: str, page_content: Dict[str, str]
    ) -> bool:
        """Update the extracted text for a content item.

        Args:
            content_id: ID of the content.
            extracted_text: Full extracted text.
            page_content: Dictionary of page/slide numbers to content.

        Returns:
            True if successful, False otherwise.
        """
        update_dict = {
            "extracted_text": extracted_text,
            "page_content": page_content,
            "updated_at": datetime.now().isoformat(),
        }

        return self.firestore.update_document(self.collection, content_id, update_dict)

    def update_file_path(self, content_id: str, file_path: str) -> bool:
        """Update the file path for a content item.

        Args:
            content_id: ID of the content.
            file_path: Path to the file.

        Returns:
            True if successful, False otherwise.
        """
        update_dict = {"file_path": file_path, "updated_at": datetime.now().isoformat()}

        return self.firestore.update_document(self.collection, content_id, update_dict)

    def _to_content_model(self, doc: Dict[str, Any]) -> ContentInDB:
        """Convert a Firestore document to a ContentInDB model.

        Args:
            doc: Firestore document data.

        Returns:
            ContentInDB model.
        """
        # Convert string dates to datetime objects if needed
        created_at = doc.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        else:
            created_at = datetime.now()  # Default if missing

        updated_at = doc.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        else:
            updated_at = datetime.now()  # Default if missing

        # Get document ID (either from id field or from the doc.id)
        doc_id = doc.get("id") or ""

        # Get required fields with defaults to avoid type errors
        title = doc.get("title") or ""
        content_type = doc.get("content_type") or ""
        tags = doc.get("tags") or []
        metadata = doc.get("metadata") or {}
        used = bool(doc.get("used", False))

        # Create ContentInDB model
        return ContentInDB(
            id=doc_id,
            title=title,
            description=doc.get("description"),
            content_type=content_type,
            source=doc.get("source", "upload"),
            file_path=doc.get("file_path"),
            drive_id=doc.get("drive_id"),
            drive_link=doc.get("drive_link"),
            tags=tags,
            metadata=metadata,
            extracted_text=doc.get("extracted_text"),
            page_content=doc.get("page_content"),
            used=used,
            embedding_id=doc.get("embedding_id"),
            created_at=created_at,
            updated_at=updated_at,
        )
