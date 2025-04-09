"""
Google Firestore client for database operations.
"""
import logging
import os
from typing import Any, Dict, List, Optional

from google.cloud import firestore

from app.core.config import settings

# Setup logging
logger = logging.getLogger(__name__)


class FirestoreClient:
    """Client for Google Firestore database operations."""

    def __init__(self):
        """Initialize the Firestore client."""
        try:
            # Check if credentials file path is provided
            credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

            if credentials_path and os.path.exists(credentials_path):
                # Use service account credentials file
                self.db = firestore.Client()
                logger.info("Initialized Firestore client with credentials file")
            else:
                # For development/testing, use mock or local emulator
                if settings.FIRESTORE_EMULATOR_HOST:
                    os.environ["FIRESTORE_EMULATOR_HOST"] = settings.FIRESTORE_EMULATOR_HOST
                    self.db = firestore.Client(project=settings.FIRESTORE_PROJECT_ID)
                    logger.info(
                        f"Initialized Firestore client with emulator at {settings.FIRESTORE_EMULATOR_HOST}"
                    )
                else:
                    # Fallback to application default credentials or implicit environment setup
                    self.db = firestore.Client(project=settings.FIRESTORE_PROJECT_ID)
                    logger.info("Initialized Firestore client with application default credentials")
        except Exception as e:
            logger.error(f"Failed to initialize Firestore client: {str(e)}")
            raise

    def get_document(self, collection: str, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a document from Firestore.

        Args:
            collection: Collection name.
            document_id: Document ID.

        Returns:
            Document data or None if not found.
        """
        try:
            doc_ref = self.db.collection(collection).document(document_id)
            doc = doc_ref.get()

            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error getting document {document_id} from {collection}: {str(e)}")
            return None

    def list_documents(
        self,
        collection: str,
        limit: int = 100,
        offset: int = 0,
        order_by: Optional[str] = None,
        filters: Optional[List[tuple[Any, ...]]] = None,
    ) -> List[Dict[str, Any]]:
        """List documents from a collection with optional filtering.

        Args:
            collection: Collection name.
            limit: Maximum number of documents to return.
            offset: Number of documents to skip.
            order_by: Field to order by.
            filters: List of filter tuples (field, op, value).

        Returns:
            List of document data.
        """
        try:
            # Start with the collection reference
            query = self.db.collection(collection)

            # Apply filters if provided
            if filters:
                for field, op, value in filters:
                    query = query.where(field, op, value)

            # Apply order if provided
            if order_by:
                query = query.order_by(order_by)

            # Apply pagination
            if offset > 0:
                # Firestore doesn't have a direct offset, so we need to use a limit+start approach
                # This is not as efficient for large offsets
                query = query.limit(offset + limit).offset(offset)
            else:
                query = query.limit(limit)

            # Execute query
            docs = query.stream()

            # Convert to list of dictionaries with document ID
            results = []
            for doc in docs:
                doc_data = doc.to_dict()
                doc_data["id"] = doc.id  # Add document ID to the data
                results.append(doc_data)

            return results
        except Exception as e:
            logger.error(f"Error listing documents from {collection}: {str(e)}")
            return []

    def create_document(self, collection: str, document_id: str, data: Dict[str, Any]) -> bool:
        """Create a document in Firestore.

        Args:
            collection: Collection name.
            document_id: Document ID.
            data: Document data.

        Returns:
            True if successful, False otherwise.
        """
        try:
            doc_ref = self.db.collection(collection).document(document_id)
            doc_ref.set(data)
            logger.info(f"Created document {document_id} in {collection}")
            return True
        except Exception as e:
            logger.error(f"Error creating document {document_id} in {collection}: {str(e)}")
            return False

    def update_document(self, collection: str, document_id: str, data: Dict[str, Any]) -> bool:
        """Update a document in Firestore.

        Args:
            collection: Collection name.
            document_id: Document ID.
            data: Document data to update.

        Returns:
            True if successful, False otherwise.
        """
        try:
            doc_ref = self.db.collection(collection).document(document_id)
            doc_ref.update(data)
            logger.info(f"Updated document {document_id} in {collection}")
            return True
        except Exception as e:
            logger.error(f"Error updating document {document_id} in {collection}: {str(e)}")
            return False

    def delete_document(self, collection: str, document_id: str) -> bool:
        """Delete a document from Firestore.

        Args:
            collection: Collection name.
            document_id: Document ID.

        Returns:
            True if successful, False otherwise.
        """
        try:
            doc_ref = self.db.collection(collection).document(document_id)
            doc_ref.delete()
            logger.info(f"Deleted document {document_id} from {collection}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document {document_id} from {collection}: {str(e)}")
            return False

    def search_documents(
        self,
        collection: str,
        query_text: str,
        fields: List[str],
        limit: int = 100,
        filters: Optional[List[tuple[Any, ...]]] = None,
    ) -> List[Dict[str, Any]]:
        """Search for documents containing the query text in specified fields.

        Note: This is a simplified search that works for small collections.
        For production, consider using a dedicated search service like
        Elasticsearch or Google's Vector Search.

        Args:
            collection: Collection name.
            query_text: Text to search for.
            fields: Fields to search in.
            limit: Maximum number of results.
            filters: Additional filters to apply.

        Returns:
            List of matching documents.
        """
        try:
            # Get all documents that match any filters
            all_docs = self.list_documents(collection, limit=limit, filters=filters)

            # If no query, return all filtered documents
            if not query_text:
                return all_docs

            # Filter documents based on text match
            query_lower = query_text.lower()
            results = []

            for doc in all_docs:
                # Check each field for text match
                for field in fields:
                    if field in doc and isinstance(doc[field], str):
                        if query_lower in doc[field].lower():
                            results.append(doc)
                            break
                    elif field in doc and isinstance(doc[field], list):
                        # Handle list fields (like tags)
                        if any(query_lower in str(item).lower() for item in doc[field]):
                            results.append(doc)
                            break

            return results[:limit]
        except Exception as e:
            logger.error(f"Error searching documents in {collection}: {str(e)}")
            return []
