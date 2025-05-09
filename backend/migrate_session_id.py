#!/usr/bin/env python
"""
Migration script to standardize field names in Firestore to use snake_case.
This ensures consistent field naming across the database.
"""
import logging
import os
from typing import Dict, Any, List

from app.db.firestore_client import FirestoreClient
from app.core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def standardize_field_names():
    """
    Standardize field names in all documents to use snake_case.
    """
    try:
        # Initialize Firestore client
        firestore = FirestoreClient()
        collection = settings.FIRESTORE_COLLECTION_CONTENT.lower()
        
        logger.info(f"Starting field name standardization for collection: {collection}")
        
        # Get all documents
        all_docs = firestore.list_documents(collection, limit=1000)
        logger.info(f"Found {len(all_docs)} documents to process")
        
        # These are the camelCase fields we know might be in documents
        camel_case_fields = [
            "sessionId", "contentType", "createdAt", "updatedAt", 
            "filePath", "driveId", "driveLink", "demoType", 
            "durationMinutes", "extractedText", "pageContent", 
            "embeddingId", "aiTags", "isLatest", "isRecommended",
            "learningLevel", "targetJobRoles", "areasOfInterest",
            "presentationSlidesUrl", "recapSlidesUrl", "sessionRecordingStatus",
            "videoSourceFileUrl", "videoYoutubeUrl", "youtubeUrl"
        ]
        
        # Map of camelCase to snake_case
        field_mapping = {
            camel: ''.join(['_' + c.lower() if c.isupper() else c for c in camel]).lstrip('_')
            for camel in camel_case_fields
        }
        
        updated_count = 0
        skipped_count = 0
        
        for doc in all_docs:
            doc_id = doc.get("id")
            updates = {}
            needs_update = False
            
            # Special handling for sessionId - add snake_case version but DON'T remove camelCase
            # During transition period, we'll use both to ensure backward compatibility
            if "sessionId" in doc and doc.get("sessionId") is not None:
                # Add snake_case version if it doesn't exist
                if "session_id" not in doc:
                    updates["session_id"] = doc.get("sessionId")
                    needs_update = True
                    logger.info(f"Adding 'session_id' while keeping 'sessionId' in doc {doc_id}")
            
            # Check for all other camelCase fields
            for camel_field, snake_field in field_mapping.items():
                # Skip sessionId as we handle it separately
                if camel_field == "sessionId":
                    continue
                    
                camel_value = doc.get(camel_field)
                
                # If camelCase field exists
                if camel_value is not None:
                    # Add snake_case version if it doesn't exist
                    if snake_field not in doc:
                        updates[snake_field] = camel_value
                        needs_update = True
                        logger.info(f"Converting '{camel_field}' to '{snake_field}' in doc {doc_id}")
                    
                    # Remove camelCase version (only if snake_case exists or we're adding it)
                    if snake_field in doc or needs_update:
                        # Use None to indicate deletion
                        updates[camel_field] = firestore.DELETE_FIELD
                        needs_update = True
                        logger.info(f"Removing '{camel_field}' from doc {doc_id}")
            
            if not needs_update:
                skipped_count += 1
                continue
            
            # Apply updates if needed
            if updates:
                success = firestore.update_document(collection, doc_id, updates)
                if success:
                    updated_count += 1
                    logger.info(f"Successfully updated document {doc_id}")
                else:
                    logger.error(f"Failed to update document {doc_id}")
        
        logger.info(f"Migration complete. Updated {updated_count} documents. Skipped {skipped_count} documents.")
        return updated_count
    
    except Exception as e:
        logger.error(f"Error in migration: {str(e)}", exc_info=True)
        return 0

if __name__ == "__main__":
    logger.info("Starting field name standardization")
    count = standardize_field_names()
    logger.info(f"Migration completed. Successfully standardized {count} documents.") 