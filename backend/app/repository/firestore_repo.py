"""Firestore repository for data storage and retrieval."""

import logging
import datetime
import os.path
import os
from typing import List, Dict, Optional, Any, Union
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

# Initialize logger
logger = logging.getLogger(__name__)

class FirestoreRepository:
    """Repository for Firestore operations."""
    
    def __init__(self):
        """Initialize the Firestore repository."""
        self._initialize_firestore()
    
    def _initialize_firestore(self):
        """Initialize Firestore client."""
        try:
            # First check if we're running in Cloud Shell with environment variables
            if 'GOOGLE_CLOUD_PROJECT' in os.environ:
                project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
                logger.info(f"Using environment variables for authentication with project: {project_id}")
                # In Cloud Shell, default credentials should work without a credentials file
                if not firebase_admin._apps:
                    firebase_admin.initialize_app()
                
                self.db = firestore.client()
                self.initialized = True
                logger.info("Firestore initialized successfully using Cloud Shell credentials")
                return
                
            # If not in Cloud Shell, check for credentials file
            if not os.path.exists('credentials.json'):
                logger.warning("Credentials file not found. Running in development mode.")
                self.db = None
                self.initialized = False
                return
                
            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                cred = credentials.Certificate('credentials.json')
                firebase_admin.initialize_app(cred)
            
            self.db = firestore.client()
            self.initialized = True
            logger.info("Firestore initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Firestore: {e}")
            logger.warning("Running in development mode with no Firestore connection")
            self.db = None
            self.initialized = False
    
    def store_content(self, content_id: str, content_data: Dict[str, Any]) -> bool:
        """Store content in Firestore.
        
        Args:
            content_id: The ID for the content
            content_data: The content data to store
            
        Returns:
            bool: Success status
        """
        if not self.initialized:
            logger.warning("Firestore not initialized, cannot store content")
            return False
        
        try:
            self.db.collection('content').document(content_id).set(content_data)
            logger.info(f"Content stored in Firestore with ID: {content_id}")
            return True
        except Exception as e:
            logger.error(f"Error storing content in Firestore: {e}")
            return False
    
    def update_content(self, content_id: str, update_data: Dict[str, Any]) -> bool:
        """Update content in Firestore.
        
        Args:
            content_id: The ID for the content
            update_data: The data to update
            
        Returns:
            bool: Success status
        """
        if not self.initialized:
            logger.warning("Firestore not initialized, cannot update content")
            return False
        
        try:
            # Add updated_at timestamp
            update_data["updated_at"] = datetime.datetime.now()
            
            self.db.collection('content').document(content_id).update(update_data)
            logger.info(f"Content updated in Firestore with ID: {content_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating content in Firestore: {e}")
            return False
    
    def get_content(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get content by ID.
        
        Args:
            content_id: The ID for the content
            
        Returns:
            Optional[Dict]: The content data or None if not found
        """
        if not self.initialized:
            logger.warning("Firestore not initialized, cannot get content")
            return None
        
        try:
            doc = self.db.collection('content').document(content_id).get()
            if doc.exists:
                return doc.to_dict()
            else:
                logger.warning(f"Content not found with ID: {content_id}")
                return None
        except Exception as e:
            logger.error(f"Error getting content from Firestore: {e}")
            return None
    
    def get_contents_by_ids(self, content_ids: List[str]) -> List[Dict[str, Any]]:
        """Get multiple content items by their IDs.
        
        Args:
            content_ids: List of content IDs
            
        Returns:
            List[Dict]: List of content items
        """
        if not self.initialized:
            logger.warning("Firestore not initialized, cannot get contents")
            return []
        
        contents = []
        
        try:
            for content_id in content_ids:
                doc = self.db.collection('content').document(content_id).get()
                if doc.exists:
                    contents.append(doc.to_dict())
            
            return contents
        except Exception as e:
            logger.error(f"Error getting contents from Firestore: {e}")
            return []
    
    def get_recent_content(self, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """Get recent content with pagination.
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Dict: Paginated content result
        """
        if not self.initialized:
            logger.warning("Firestore not initialized, cannot get recent content")
            return {
                "content": [],
                "totalCount": 0,
                "page": page,
                "pageSize": page_size
            }
        
        try:
            # Get total count (inefficient for large collections)
            total_count = len(list(self.db.collection('content').stream()))
            
            # Get paginated results
            offset = (page - 1) * page_size
            docs = (
                self.db.collection('content')
                .order_by("created_at", direction=firestore.Query.DESCENDING)
                .limit(page_size)
                .offset(offset)
                .stream()
            )
            
            contents = [doc.to_dict() for doc in docs]
            
            return {
                "content": contents,
                "totalCount": total_count,
                "page": page,
                "pageSize": page_size
            }
        except Exception as e:
            logger.error(f"Error getting recent content from Firestore: {e}")
            return {
                "content": [],
                "totalCount": 0,
                "page": page,
                "pageSize": page_size,
                "error": str(e)
            }
    
    def get_popular_tags(self, limit: int = 20) -> List[str]:
        """Get most popular tags.
        
        Args:
            limit: Maximum number of tags to return
            
        Returns:
            List[str]: List of popular tags
        """
        if not self.initialized:
            logger.warning("Firestore not initialized, cannot get popular tags")
            return []
        
        try:
            # Collect all tags
            all_tags = []
            docs = self.db.collection('content').stream()
            
            for doc in docs:
                content = doc.to_dict()
                tags = content.get("metadata", {}).get("tags", [])
                all_tags.extend(tags)
            
            # Count frequencies
            tag_counts = {}
            for tag in all_tags:
                if tag in tag_counts:
                    tag_counts[tag] += 1
                else:
                    tag_counts[tag] = 1
            
            # Sort by frequency and limit
            popular_tags = sorted(tag_counts.keys(), key=lambda x: tag_counts[x], reverse=True)[:limit]
            
            return popular_tags
        except Exception as e:
            logger.error(f"Error getting popular tags from Firestore: {e}")
            return []
    
    def find_content_by_filters(self, filters: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """Find content by filters.
        
        Args:
            filters: Dictionary of filters
            limit: Maximum number of results
            
        Returns:
            List[Dict]: Filtered content
        """
        if not self.initialized:
            logger.warning("Firestore not initialized, cannot filter content")
            return []
        
        try:
            query = self.db.collection('content')
            
            # Apply filters
            if filters:
                if "tracks" in filters and filters["tracks"]:
                    query = query.where(filter=FieldFilter("metadata.track", "in", filters["tracks"]))
                if "tags" in filters and filters["tags"]:
                    # This is a simplification - array-contains-any is limited to 10 values
                    query = query.where(filter=FieldFilter("metadata.tags", "array_contains_any", filters["tags"][:10]))
            
            # Execute query
            docs = query.limit(limit).stream()
            contents = [doc.to_dict() for doc in docs]
            
            return contents
        except Exception as e:
            logger.error(f"Error finding content by filters: {e}")
            return []
    
    def list_contents(self):
        """List all content documents.
        
        Returns:
            List[Dict]: List of content documents
        """
        try:
            if not self.initialized:
                logger.warning("Firestore repository not initialized, returning empty list")
                return []
            
            # Get all documents from the content collection
            docs = self.db.collection('content').stream()
            contents = []
            
            for doc in docs:
                content = doc.to_dict()
                # Ensure ID is included
                if 'id' not in content:
                    content['id'] = doc.id
                contents.append(content)
            
            logger.info(f"Retrieved {len(contents)} contents from Firestore")
            return contents
        except Exception as e:
            logger.error(f"Error listing contents: {e}")
            return [] 