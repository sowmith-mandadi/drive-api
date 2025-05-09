"""
Google Firestore client for database operations.
"""
import logging
import os
import traceback
from typing import Any, Dict, List, Optional, Tuple

from google.cloud import firestore

from app.core.config import settings

# Setup logging
logger = logging.getLogger(__name__)


class FirestoreClient:
    """Client for Google Firestore database operations."""

    # Special value to indicate field deletion
    DELETE_FIELD = firestore.DELETE_FIELD

    def __init__(self) -> None:
        """Initialize the Firestore client."""
        try:
            # Check if we should use App Engine credentials
            use_app_engine_creds = (
                os.environ.get("USE_APP_ENGINE_CREDENTIALS", "").lower() == "true"
            )

            logger.info(
                f"Initializing Firestore client - use_app_engine_creds: {use_app_engine_creds}"
            )

            # Detect App Engine environment
            is_app_engine = (
                os.environ.get("GAE_ENV") == "standard"
                or os.environ.get("GAE_APPLICATION") is not None
            )

            if is_app_engine:
                logger.info("Detected App Engine environment")

            # Get project ID from environment variables
            project_id = settings.FIRESTORE_PROJECT_ID
            if not project_id:
                project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
                logger.info(f"Using GOOGLE_CLOUD_PROJECT: {project_id}")

            # Clear any empty GOOGLE_APPLICATION_CREDENTIALS environment variable
            # This forces the client to use the App Engine default credentials
            if (
                "GOOGLE_APPLICATION_CREDENTIALS" in os.environ
                and not os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
            ):
                logger.info(
                    "Removing empty GOOGLE_APPLICATION_CREDENTIALS to force default credentials"
                )
                del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

            # Initialize Firestore client with project ID only
            logger.info(f"Initializing Firestore with project ID: {project_id}")
            self.db = firestore.Client(project=project_id)
            logger.info("Successfully connected to Firestore with default credentials")

            # Verify connection with a simple query
            try:
                # Try to access a collection to verify connection
                self.db.collection("_verification").limit(1).get()
                logger.info("Firestore connection verified successfully")
            except Exception as verify_error:
                logger.warning(
                    f"Firestore client initialized but connection verification failed: {str(verify_error)}",
                    exc_info=True,
                )

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
                data = doc.to_dict()
                data["id"] = doc.id  # Add document ID
                return data
            else:
                logger.warning(f"Document {document_id} not found in {collection}")
                return None
        except Exception as e:
            logger.error(f"Error fetching document {document_id} from {collection}: {str(e)}")
            return None

    def generate_id(self) -> str:
        """Generate a new document ID.

        Returns:
            A new document ID.
        """
        return self.db.collection("_ids").document().id

    def list_documents(
        self,
        collection: str,
        limit: int = 100,
        offset: int = 0,
        order_by: Optional[str] = None,
        filters: Optional[List[Tuple[str, str, Any]]] = None,
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
            print(f"DEBUG (Firestore): Listing from collection '{collection}' with limit={limit}, offset={offset}, order_by='{order_by}'")
            # Start with the collection reference
            query = self.db.collection(collection)

            # Apply filters if provided
            if filters:
                for field, op, value in filters:
                    query = query.where(field, op, value)
                    print(f"DEBUG (Firestore): Added filter {field} {op} {value}")

            # Apply order if provided
            if order_by:
                query = query.order_by(order_by)
                print(f"DEBUG (Firestore): Ordering by '{order_by}'")

            # Apply pagination
            if offset > 0:
                # Firestore doesn't have a direct offset, so we need to use a limit+start approach
                # This is not as efficient for large offsets
                query = query.limit(offset + limit).offset(offset)
                print(f"DEBUG (Firestore): Using offset={offset}")
            else:
                query = query.limit(limit)

            # Execute query
            print(f"DEBUG (Firestore): Executing query...")
            
            try:
                # Try to execute the query with the ordering
                docs = query.stream()
                
                # Convert to list of dictionaries with document ID
                results = []
                for doc in docs:
                    doc_data = doc.to_dict()
                    doc_data["id"] = doc.id  # Add document ID to the data
                    results.append(doc_data)
                
                print(f"DEBUG (Firestore): Query returned {len(results)} documents")
                
                # If no results and we were trying to order by a field, try again without ordering
                if len(results) == 0 and order_by:
                    print(f"DEBUG (Firestore): No results with ordering, trying without ordering")
                    return self.list_documents(collection, limit, offset, None, filters)
                
                return results
                
            except Exception as query_error:
                print(f"DEBUG (Firestore): Error executing query, possibly invalid order_by field: {str(query_error)}")
                # If ordering caused the error, try again without ordering
                if order_by:
                    print(f"DEBUG (Firestore): Retrying without ordering")
                    return self.list_documents(collection, limit, offset, None, filters)
                else:
                    # If there was an error and we weren't ordering, re-raise
                    raise

            # Check if collection exists with a direct approach
            try:
                # Check if this collection even exists by doing a count
                count_query = self.db.collection(collection).limit(1)
                count_docs = list(count_query.stream())
                if not count_docs:
                    print(f"DEBUG (Firestore): Collection '{collection}' appears to be empty or doesn't exist")
                else:
                    print(f"DEBUG (Firestore): Collection '{collection}' exists and contains documents")
            except Exception as count_error:
                print(f"DEBUG (Firestore): Error checking collection existence: {str(count_error)}")

        except Exception as e:
            print(f"DEBUG (Firestore): Error listing documents from {collection}: {str(e)}")
            logger.error(f"Error listing documents from {collection}: {str(e)}")
            return []

    def list_documents_by_field(
        self, collection: str, field: str, value: Any, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """List documents by a specific field value.

        This is a convenience method for the common use case of querying by a single field.

        Args:
            collection: Collection name.
            field: Field name to filter by.
            value: Field value to match.
            limit: Maximum number of documents to return.

        Returns:
            List of document data.
        """
        try:
            # Use a filter tuple for the field
            filters = [(field, "==", value)]
            return self.list_documents(collection, limit=limit, filters=filters)
        except Exception as e:
            logger.error(f"Error listing documents by field {field} from {collection}: {str(e)}")
            return []

    def create_document(
        self, collection: str, document_id: str, data: Dict[str, Any]
    ) -> bool:
        """Create a document in Firestore.

        Args:
            collection: Collection name.
            document_id: Document ID (empty string to auto-generate).
            data: Document data.

        Returns:
            True if successful, False otherwise.
        """
        try:
            # If document_id is empty, auto-generate one
            if not document_id:
                document_id = self.generate_id()

            # Set the document
            self.db.collection(collection).document(document_id).set(data)
            logger.info(f"Created document {document_id} in {collection}")
            return True
        except Exception as e:
            logger.error(f"Error creating document in {collection}: {str(e)}")
            return False

    def update_document(
        self, collection: str, document_id: str, data: Dict[str, Any]
    ) -> bool:
        """Update a document in Firestore.

        Args:
            collection: Collection name.
            document_id: Document ID.
            data: Document data to update.

        Returns:
            True if successful, False otherwise.
        """
        try:
            # Update the document
            self.db.collection(collection).document(document_id).update(data)
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
        query: str,
        search_fields: List[str],
        filters: Optional[List[Tuple[str, str, Any]]] = None,
        limit: int = 100,
        offset: int = 0,
        order_by: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search for documents using a combined approach of filters and simple text matching.

        Args:
            collection: Collection name.
            query: Text query.
            search_fields: Fields to search in.
            filters: List of filter tuples (field, operator, value).
            limit: Maximum number of results.
            offset: Number of results to skip.
            order_by: Field to order by.

        Returns:
            List of document dictionaries.
        """
        try:
            if not collection:
                logger.error("Collection name cannot be empty")
                return []

            if not isinstance(query, str):
                query = str(query) if query is not None else ""

            # Start query
            ref = self.db.collection(collection)
            search_query = ref

            # Apply filters if provided
            if filters:
                for field, op, value in filters:
                    search_query = search_query.where(field, op, value)

            # Apply ordering if specified
            if order_by:
                search_query = search_query.order_by(order_by, direction=firestore.Query.DESCENDING)

            # Apply limit and offset
            search_query = search_query.limit(limit).offset(offset)

            # Execute query
            docs = list(search_query.stream())
            
            result_docs = []
            for doc in docs:
                doc_dict = doc.to_dict()
                # Add document ID as a field
                doc_dict["id"] = doc.id
                result_docs.append(doc_dict)

            # No full-text search in basic Firestore, but we can simulate it
            if query and search_fields:
                query = query.lower()
                filtered_docs = []
                # Simple text filtering
                for doc in result_docs:
                    for field in search_fields:
                        if field in doc:
                            field_value = doc[field]
                            if isinstance(field_value, str) and query in field_value.lower():
                                filtered_docs.append(doc)
                                break
                            elif isinstance(field_value, list):
                                # Handle list fields (like tags)
                                for item in field_value:
                                    if isinstance(item, str) and query in item.lower():
                                        filtered_docs.append(doc)
                                        break
                return filtered_docs
            
            return result_docs
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []
