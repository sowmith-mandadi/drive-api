#!/usr/bin/env python3
"""
Script to generate an indexing payload for content API.

This script reads content from Firestore and creates a JSON payload that matches
the structure required by the indexing API. It handles YouTube videos and 
presentations correctly, grouping files by session ID.

Usage:
    python generate_index_payload.py --credentials credentials.json --output payload.json
"""

import argparse
import json
import logging
import os
import sys
import uuid
from collections import defaultdict
from typing import Dict, List, Any, Optional

from google.cloud import firestore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class IndexPayloadGenerator:
    """Generates index payload from Firestore data."""

    def __init__(self, credentials_path=None):
        """
        Initialize the payload generator.
        
        Args:
            credentials_path: Path to the service account credentials file
        """
        # Set credentials environment variable if provided
        if credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
            logger.info(f"Using credentials from: {credentials_path}")
            
        # Connect to Firestore
        try:
            self.db = firestore.Client()
            project_id = self.db.project
            logger.info(f"Connected to Firestore project: {project_id}")
            print(f"Connected to Firestore project: {project_id}")
        except Exception as e:
            logger.error(f"Failed to connect to Firestore: {e}")
            print(f"Error: Failed to connect to Firestore: {e}")
            sys.exit(1)

    def get_content_documents(self, collection: str = "content", limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve content documents from Firestore.

        Args:
            collection: Collection name to query
            limit: Maximum number of documents to retrieve

        Returns:
            List of content documents
        """
        try:
            # Query the content collection
            docs = list(self.db.collection(collection).limit(limit).get())
            
            # Convert to list of dictionaries with document ID
            results = []
            for doc in docs:
                doc_data = doc.to_dict()
                doc_data["id"] = doc.id  # Add document ID
                results.append(doc_data)
            
            logger.info(f"Retrieved {len(results)} documents from {collection}")
            print(f"Retrieved {len(results)} documents from {collection}")
            return results
        except Exception as e:
            logger.error(f"Error retrieving documents from {collection}: {e}")
            print(f"Error retrieving documents: {e}")
            return []

    def get_content_by_id(self, content_id: str, collection: str = "content") -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific content document by ID.
        
        Args:
            content_id: The content ID to retrieve
            collection: Collection name to query
            
        Returns:
            Content document or None if not found
        """
        try:
            doc = self.db.collection(collection).document(content_id).get()
            if doc.exists:
                doc_data = doc.to_dict()
                doc_data["id"] = doc.id
                return doc_data
            else:
                logger.error(f"Content not found with ID: {content_id}")
                return None
        except Exception as e:
            logger.error(f"Error retrieving content {content_id}: {e}")
            return None

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
        
        for file_info in fileUrls:
            # Skip drive folders - we don't need them for indexing
            if file_info.get("contentType") == "folder" or file_info.get("presentation_type") == "drive_folder":
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
                # Fallback to url field if gcs_path not available
                elif file_info.get("url"):
                    file_entry["file_url"] = file_info.get("url")
            
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
                default_entry["file_url"] = presentation_url  # Use same URL for both since we don't have GCS URL
            elif recap_url:
                default_entry["drive_url"] = recap_url
                default_entry["file_url"] = recap_url  # Use same URL for both since we don't have GCS URL
            elif video_url:
                default_entry["drive_url"] = video_url
                default_entry["file_url"] = video_url  # For YouTube, both are the same
            
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
        
        return file_entries

    def generate_payloads(self, limit: int = 100, collection: str = "content", content_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Generate index payloads grouped by session ID.

        Args:
            limit: Maximum number of content items to include
            collection: Collection to query for content items
            content_id: Optional content ID to filter by

        Returns:
            List of payloads, one per session ID
        """
        # Get content documents
        content_items = []
        if content_id:
            # If specific content ID is provided, get just that document
            doc = self.get_content_by_id(content_id, collection)
            if doc:
                content_items = [doc]
                logger.info(f"Retrieved document with ID {content_id}")
            else:
                return []
        else:
            # Otherwise get all documents up to the limit
            content_items = self.get_content_documents(collection, limit)
        
        # Group content by session ID
        session_content_map = defaultdict(list)
        
        for item in content_items:
            # Get sessionId, or use content ID if no sessionId
            session_id = item.get("sessionId")
            if not session_id:
                session_id = item.get("id", str(uuid.uuid4()))
            
            # Add to the appropriate session group
            session_content_map[session_id].append(item)
        
        # Generate one payload per session ID
        payloads = []
        
        for session_id, items in session_content_map.items():
            # Generate a payload for this session
            file_list = []
            
            # Process each content item in this session
            for item in items:
                # Create file entries for this content item
                entries = self.create_file_entries(item)
                file_list.extend(entries)
            
            # Only create a payload if we have files to index
            if file_list:
                payload = {
                    "session_id": session_id,
                    "file_list": file_list
                }
                payloads.append(payload)
        
        logger.info(f"Generated {len(payloads)} payloads for {len(content_items)} content items")
        return payloads

    def save_payloads(self, payloads: List[Dict[str, Any]], output_dir: str = "./payloads"):
        """
        Save the payloads to JSON files.

        Args:
            payloads: List of index payloads
            output_dir: Directory to save the payload files
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Save each payload to a separate file
            for i, payload in enumerate(payloads):
                session_id = payload["session_id"]
                file_path = os.path.join(output_dir, f"{session_id}.json")
                
                with open(file_path, 'w') as f:
                    json.dump(payload, f, indent=2)
                logger.info(f"Saved payload for session {session_id} to {file_path}")
                print(f"Saved payload for session {session_id} to {file_path}")
                print(f"Total files in payload: {len(payload['file_list'])}")
                
        except Exception as e:
            logger.error(f"Error saving payloads: {e}")
            print(f"Error saving payloads: {e}")

    def send_to_indexer(self, payload: Dict[str, Any], endpoint_url: str):
        """
        Send the payload to the indexer API.

        Args:
            payload: The index payload
            endpoint_url: The indexer API endpoint URL
        
        Returns:
            True if successful, False otherwise
        """
        try:
            import requests
            
            print(f"Sending payload to indexer API: {endpoint_url}")
            print(f"Payload contains {len(payload['file_list'])} files for session {payload['session_id']}")
            
            response = requests.post(
                endpoint_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Successfully sent payload to indexer: {response.status_code}")
                print(f"Success! API responded with status code: {response.status_code}")
                try:
                    print(f"Response: {response.json()}")
                except:
                    print(f"Response: {response.text}")
                return True
            else:
                logger.error(f"Failed to send payload: {response.status_code} - {response.text}")
                print(f"Error! API responded with status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error sending payload to indexer: {e}")
            print(f"Failed to send payload: {e}")
            return False

    def send_all_payloads(self, payloads: List[Dict[str, Any]], endpoint_url: str):
        """
        Send all payloads to the indexer API.
        
        Args:
            payloads: List of index payloads
            endpoint_url: The indexer API endpoint URL
            
        Returns:
            Tuple of (success_count, total_count)
        """
        if not endpoint_url:
            print("No endpoint URL provided")
            return 0, len(payloads)
            
        success_count = 0
        
        for payload in payloads:
            if self.send_to_indexer(payload, endpoint_url):
                success_count += 1
        
        return success_count, len(payloads)


def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description="Generate index payload from Firestore content")
    parser.add_argument("--credentials", help="Path to service account credentials file")
    parser.add_argument("--collection", default="content", help="Collection name to use")
    parser.add_argument("--content-id", help="Specific content ID to process")
    parser.add_argument("--limit", type=int, default=100, help="Maximum number of documents to process")
    parser.add_argument("--output-dir", default="./payloads", help="Output directory path")
    parser.add_argument("--endpoint", help="Indexer API endpoint URL")
    
    args = parser.parse_args()
    
    # Initialize the generator with credentials
    generator = IndexPayloadGenerator(credentials_path=args.credentials)
    
    # Generate payloads
    print(f"Generating indexing payloads from '{args.collection}' collection...")
    payloads = generator.generate_payloads(
        limit=args.limit,
        collection=args.collection,
        content_id=args.content_id
    )
    
    # Display summary of generated payloads
    print(f"Generated {len(payloads)} payloads")
    
    # Save payloads to files
    generator.save_payloads(payloads, args.output_dir)
    
    # Send to indexer if endpoint provided
    if args.endpoint:
        success_count, total_count = generator.send_all_payloads(payloads, args.endpoint)
        print(f"Sent {success_count}/{total_count} payloads to indexer API")


if __name__ == "__main__":
    main() 