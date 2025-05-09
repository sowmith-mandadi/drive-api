"""
Service for generating indexing payloads and sending them to the indexer API.
"""
import json
import logging
import os
import uuid
from collections import defaultdict
from typing import Dict, List, Any, Optional, Tuple

import requests

from app.core.config import settings
from app.core.logging import configure_logging
from app.db.firestore_client import FirestoreClient

# Setup logging
logger = configure_logging()

class IndexService:
    """Service for generating and sending indexing payloads."""

    def __init__(self) -> None:
        """Initialize the index service."""
        try:
            logger.info("Initializing IndexService")

            # Initialize Firestore client
            try:
                self.firestore = FirestoreClient()
                logger.info("IndexService: Firestore client initialized successfully")
            except Exception as db_error:
                logger.error(
                    f"IndexService: Failed to initialize Firestore client: {str(db_error)}",
                    exc_info=True,
                )
                # Re-raise to fail initialization
                raise

            # Get indexer API endpoint from settings or environment variables
            self.indexer_endpoint = os.environ.get(
                "INDEXER_API_ENDPOINT", settings.INDEXER_API_ENDPOINT
            )
            if not self.indexer_endpoint:
                logger.warning(
                    "IndexService: No indexer API endpoint configured - indexing will be disabled"
                )

            logger.info("IndexService initialization completed successfully")

        except Exception as e:
            logger.error(f"Critical error initializing IndexService: {str(e)}", exc_info=True)
            # Re-raise to fail initialization
            raise

    def create_file_entries(self, content_item: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create file entries for the index payload.

        Args:
            content_item: The content document from Firestore

        Returns:
            List of file entry dictionaries
        """
        # Extract file URLs from content item
        file_entries = []
        fileUrls = content_item.get("fileUrls", [])
        
        logger.info(f"Creating file entries for content ID: {content_item.get('id')}")
        logger.info(f"Found {len(fileUrls)} file URLs in the content item")
        
        for file_info in fileUrls:
            # Skip drive folders - we don't need them for indexing
            if file_info.get("contentType") == "folder" or file_info.get("presentation_type") == "drive_folder":
                logger.info(f"Skipping folder: {file_info.get('name')}")
                continue
                
            # Initialize entry with common fields - summary should be empty as it will be generated after indexing
            file_entry = {
                "is_updated": False,
                "is_summary_updated": False,
                "summary": ""
            }
            
            # Handle YouTube videos
            if (file_info.get("contentType") == "video" or 
                file_info.get("presentation_type") == "youtube_video"):
                
                # For YouTube, both drive_url and file_url are the YouTube link
                youtube_url = file_info.get("drive_url") or file_info.get("url")
                if youtube_url:
                    file_entry["drive_url"] = youtube_url
                    file_entry["file_url"] = youtube_url
                    logger.info(f"Added YouTube video: {youtube_url}")
            
            # Handle presentation files 
            elif (file_info.get("contentType") == "presentation" or
                  file_info.get("presentation_type") in ["presentation_slides", "recap_slides"]):
                
                # For presentations, drive_url is the original Google Docs link
                drive_url = file_info.get("drive_url")
                if drive_url:
                    file_entry["drive_url"] = drive_url
                
                # file_url should be the GCS bucket URL
                gcs_path = file_info.get("gcs_path")
                if gcs_path:
                    file_entry["file_url"] = gcs_path
                    logger.info(f"Added presentation with GCS path: {gcs_path}")
                # Fallback to url field if gcs_path not available
                elif file_info.get("url"):
                    file_entry["file_url"] = file_info.get("url")
                    logger.info(f"Added presentation with URL: {file_info.get('url')}")
            
            # Build metadata from the content item's metadata field if it exists
            meta_data = {}
            
            # Use the metadata field from content_item as the primary source
            if content_item.get("metadata"):
                for key, value in content_item.get("metadata", {}).items():
                    # Include only non-null and non-empty values
                    if value is not None and value != "":
                        meta_data[key] = value
            
            # Add file-specific metadata
            if file_info.get("type") is not None and file_info.get("type") != "":
                meta_data["fileType"] = file_info.get("type")
            if file_info.get("name") is not None and file_info.get("name") != "":
                meta_data["fileName"] = file_info.get("name")
            if file_info.get("size") is not None and file_info.get("size") != 0:
                meta_data["fileSize"] = file_info.get("size")
            
            # Include standard fields only if they're not already in metadata and not null/empty
            standard_fields = {
                "track": content_item.get("track", ""),
                "tags": content_item.get("tags", []),
                "sessionType": content_item.get("sessionType", ""),
                "learningLevel": content_item.get("learningLevel", ""),
                "title": content_item.get("title", ""),
                "sessionId": content_item.get("sessionId", ""),
                "durationMinutes": content_item.get("durationMinutes"),
                "sessionDate": content_item.get("sessionDate"),
                "industry": content_item.get("industry", "")
            }
            
            for key, value in standard_fields.items():
                if key not in meta_data and value is not None and value != "":
                    meta_data[key] = value
            
            file_entry["meta_data"] = meta_data
            
            # Add to list if we have required URLs
            if "drive_url" in file_entry or "file_url" in file_entry:
                file_entries.append(file_entry)
        
        # If no file URLs were found in fileUrls array, create a default entry from legacy fields
        if not file_entries:
            logger.info("No file URLs found, creating default entry from legacy fields")
            
            # Build default file entry from the content metadata - summary should be empty
            default_entry = {
                "is_updated": False,
                "is_summary_updated": False,
                "summary": ""
            }
            
            # Try to find URLs from legacy fields
            presentation_url = content_item.get("presentationSlidesUrl")
            recap_url = content_item.get("recapSlidesUrl")
            video_url = content_item.get("videoYoutubeUrl")
            
            # Set drive_url based on availability (prioritize presentation slides)
            if presentation_url:
                default_entry["drive_url"] = presentation_url
                default_entry["file_url"] = presentation_url
                logger.info(f"Using legacy presentationSlidesUrl: {presentation_url}")
            elif recap_url:
                default_entry["drive_url"] = recap_url
                default_entry["file_url"] = recap_url
                logger.info(f"Using legacy recapSlidesUrl: {recap_url}")
            elif video_url:
                default_entry["drive_url"] = video_url
                default_entry["file_url"] = video_url
                logger.info(f"Using legacy videoYoutubeUrl: {video_url}")
            
            # Build metadata from the content item's metadata field if it exists
            meta_data = {}
            
            # Use the metadata field from content_item as the primary source
            if content_item.get("metadata"):
                for key, value in content_item.get("metadata", {}).items():
                    # Include only non-null and non-empty values
                    if value is not None and value != "":
                        meta_data[key] = value
            
            # Include standard fields only if they're not already in metadata and not null/empty
            standard_fields = {
                "track": content_item.get("track", ""),
                "tags": content_item.get("tags", []),
                "sessionType": content_item.get("sessionType", ""),
                "learningLevel": content_item.get("learningLevel", ""),
                "title": content_item.get("title", ""),
                "sessionId": content_item.get("sessionId", ""),
                "durationMinutes": content_item.get("durationMinutes"),
                "sessionDate": content_item.get("sessionDate"),
                "industry": content_item.get("industry", "")
            }
            
            for key, value in standard_fields.items():
                if key not in meta_data and value is not None and value != "":
                    meta_data[key] = value
                        
            default_entry["meta_data"] = meta_data
            
            if "drive_url" in default_entry or "file_url" in default_entry:
                file_entries.append(default_entry)
        
        logger.info(f"Created {len(file_entries)} file entries for indexing")
        return file_entries

    def generate_session_payload(self, session_id: str, content_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a payload for a specific session with its content items.
        
        Args:
            session_id: The session ID for the payload
            content_items: List of content items belonging to this session
            
        Returns:
            Complete payload for the session
        """
        # Create file list with all files from all content items
        file_list = []
        
        for item in content_items:
            entries = self.create_file_entries(item)
            file_list.extend(entries)
        
        # Create the payload
        payload = {
            "session_id": session_id,
            "file_list": file_list
        }
        
        logger.info(f"Generated payload for session {session_id} with {len(file_list)} files")
        return payload

    def generate_payload_for_content(self, content_id: str) -> Optional[Dict[str, Any]]:
        """
        Generate an index payload for a specific content item.
        
        Args:
            content_id: The content ID to generate a payload for
            
        Returns:
            Payload for the session containing this content, or None if content not found
        """
        try:
            # Get the content document
            content_item = self.firestore.get_document("content", content_id)
            if not content_item:
                logger.error(f"Content not found for ID: {content_id}")
                return None
            
            # Get session ID from content item or use content ID if no session ID
            session_id = content_item.get("sessionId")
            if not session_id:
                session_id = content_id
                logger.info(f"No session ID found, using content ID as session ID: {session_id}")
            else:
                logger.info(f"Using session ID from content: {session_id}")
            
            # Check if there are other content items with the same session ID
            # to include them in the same payload
            if session_id != content_id:
                # Try to find other content items with the same session ID
                filters = [("sessionId", "==", session_id)]
                session_items = self.firestore.list_documents(
                    "content", filters=filters, limit=100
                )
                
                if session_items:
                    logger.info(f"Found {len(session_items)} content items for session {session_id}")
                    return self.generate_session_payload(session_id, session_items)
            
            # If no other items found or session ID is content ID, just use this content item
            return self.generate_session_payload(session_id, [content_item])
        
        except Exception as e:
            logger.error(f"Error generating payload for content {content_id}: {str(e)}", exc_info=True)
            return None
    
    async def send_to_indexer(self, payload: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Send the payload to the indexer API.
        
        Args:
            payload: The index payload to send
            
        Returns:
            Tuple of (success, response_data)
        """
        if not self.indexer_endpoint:
            logger.warning("No indexer endpoint configured, skipping indexing")
            return False, None
            
        try:
            logger.info(f"Sending payload to indexer API: {self.indexer_endpoint}")
            logger.info(f"Payload contains {len(payload['file_list'])} files")
            
            # Make the API request
            response = requests.post(
                self.indexer_endpoint,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            # Handle the response
            if response.status_code in [200, 201, 202]:
                logger.info(f"Successfully sent payload to indexer: {response.status_code}")
                
                # Try to parse JSON response
                try:
                    response_data = response.json()
                    return True, response_data
                except:
                    return True, {"message": response.text}
            else:
                logger.error(f"Failed to send payload: {response.status_code} - {response.text}")
                return False, {"error": f"API error: {response.status_code}", "message": response.text}
                
        except Exception as e:
            logger.error(f"Error sending payload to indexer: {str(e)}", exc_info=True)
            return False, {"error": str(e)}
    
    async def index_content(self, content_id: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Generate payload and send to indexer for a specific content ID.
        
        Args:
            content_id: ID of the content to index
            
        Returns:
            Tuple of (success, response_data)
        """
        try:
            logger.info(f"Starting indexing process for content ID: {content_id}")
            
            # Get the content to make sure it exists and has required files
            content_item = self.firestore.get_document("content", content_id)
            if not content_item:
                logger.error(f"Content not found for ID: {content_id}")
                return False, {"error": "Content not found"}
            
            # Check if the content has a GCS path in any of its fileUrls
            has_gcs_path = False
            for file_info in content_item.get("fileUrls", []):
                if file_info.get("gcs_path"):
                    has_gcs_path = True
                    break
            
            # If no GCS paths, check if we have YouTube or other URLs
            if not has_gcs_path:
                has_url = False
                for file_info in content_item.get("fileUrls", []):
                    if file_info.get("url") or file_info.get("drive_url"):
                        has_url = True
                        break
                
                if not has_url:
                    logger.warning(f"Content {content_id} has no files with GCS paths or URLs")
                    return False, {"error": "No files ready for indexing"}
            
            # Generate the payload for this content's session
            payload = self.generate_payload_for_content(content_id)
            
            # Check if we have a valid payload
            if not payload or not payload["file_list"]:
                logger.warning(f"No indexable files found for content ID: {content_id}")
                
                # Update content status with the error
                error_update = {
                    "indexing_status": "skipped",
                    "indexing_message": "No indexable files found"
                }
                self.firestore.update_document("content", content_id, error_update)
                
                return False, {"error": "No indexable files found"}
                
            # Send to indexer API
            success, response = await self.send_to_indexer(payload)
            
            # Update content document with indexing status
            status_update = {
                "indexing_status": "indexed" if success else "failed",
                "indexing_response": response
            }
            self.firestore.update_document("content", content_id, status_update)
            
            return success, response
            
        except Exception as e:
            logger.error(f"Error indexing content {content_id}: {str(e)}", exc_info=True)
            
            # Update content with error status
            error_update = {
                "indexing_status": "failed",
                "indexing_error": str(e)
            }
            self.firestore.update_document("content", content_id, error_update)
            
            return False, {"error": str(e)} 