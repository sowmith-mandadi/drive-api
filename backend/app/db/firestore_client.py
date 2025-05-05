"""
Google Firestore client for database operations.
"""
import logging
import os
import traceback
from typing import Any, Dict, List, Optional

from google.cloud import firestore

from app.core.config import settings

# Setup logging
logger = logging.getLogger(__name__)


class FirestoreClient:
    """Client for Google Firestore database operations."""

    def __init__(self) -> None:
        """Initialize the Firestore client."""
        try:
            # Check if credentials file path is provided
            credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
            
            logger.info(f"Initializing Firestore client - credentials path: {credentials_path or 'not set'}")

            if credentials_path and os.path.exists(credentials_path):
                # Use service account credentials file
                try:
                    self.db = firestore.Client()
                    logger.info("Initialized Firestore client with credentials file")
                except Exception as cred_error:
                    logger.error(
                        f"Failed to initialize Firestore with credentials file: {str(cred_error)}",
                        exc_info=True
                    )
                    # Try fallback
                    logger.info("Attempting to fall back to application default credentials")
                    self.db = firestore.Client(project=settings.FIRESTORE_PROJECT_ID)
                    logger.info("Successfully fell back to application default credentials")
            else:
                # For development/testing, use mock or local emulator
                if settings.FIRESTORE_EMULATOR_HOST:
                    try:
                        os.environ["FIRESTORE_EMULATOR_HOST"] = settings.FIRESTORE_EMULATOR_HOST
                        self.db = firestore.Client(project=settings.FIRESTORE_PROJECT_ID)
                        logger.info(
                            f"Initialized Firestore client with emulator at {settings.FIRESTORE_EMULATOR_HOST}"
                        )
                    except Exception as emu_error:
                        logger.error(
                            f"Failed to initialize Firestore with emulator: {str(emu_error)}",
                            exc_info=True
                        )
                        raise
                else:
                    # Fallback to application default credentials or implicit environment setup
                    try:
                        # Log environment details that might affect authentication
                        gcp_project = settings.FIRESTORE_PROJECT_ID
                        logger.info(f"Initializing Firestore with project ID: {gcp_project}")
                        
                        # Log authentication-related environment variables (without sensitive values)
                        auth_vars = [
                            "GOOGLE_APPLICATION_CREDENTIALS",
                            "GOOGLE_CLOUD_PROJECT",
                            "GCLOUD_PROJECT",
                            "GCP_PROJECT"
                        ]
                        for var in auth_vars:
                            if os.environ.get(var):
                                logger.info(f"Environment variable {var} is set")
                            else:
                                logger.info(f"Environment variable {var} is NOT set")
                        
                        self.db = firestore.Client(project=gcp_project)
                        logger.info("Initialized Firestore client with application default credentials")
                        
                        # Verify connection with a simple query
                        try:
                            # Try to access a collection to verify connection
                            self.db.collection("_verification").limit(1).get()
                            logger.info("Firestore connection verified successfully")
                        except Exception as verify_error:
                            logger.warning(
                                f"Firestore client initialized but connection verification failed: {str(verify_error)}",
                                exc_info=True
                            )
                            # Continue anyway, this is just a verification
                            
                    except Exception as adc_error:
                        logger.error(
                            f"Failed to initialize Firestore with application default credentials: {str(adc_error)}",
                            exc_info=True
                        )
                        raise
        except Exception as e:
            logger.error(
                f"Critical failure initializing Firestore client: {str(e)}\nTraceback: {traceback.format_exc()}"
            )
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
                # Explicitly cast the dictionary to Dict[str, Any]
                doc_dict: Dict[str, Any] = doc.to_dict() or {}
                doc_dict["id"] = doc.id  # Add document ID to the data
                return doc_dict
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

    def generate_id(self) -> str:
        """Generate a unique document ID.
        
        Returns:
            A unique document ID string.
        """
        try:
            # Use Firestore's document ID generation
            doc_ref = self.db.collection("_unused").document()
            return doc_ref.id
        except Exception as e:
            logger.error(f"Error generating document ID: {str(e)}")
            # Fallback to a timestamp-based ID if Firestore generation fails
            import uuid
            return str(uuid.uuid4())
