#!/usr/bin/env python3
"""
Script to generate an indexing payload for content API.

This script reads content from Firestore and creates a JSON payload that matches
the structure required by the indexing API. It handles YouTube videos and 
presentations correctly.

Usage:
    python generate_index_payload.py --credentials credentials.json --output payload.json
"""

import argparse
import json
import logging
import os
import sys
import uuid
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
                
            # Initialize entry with common fields
            file_entry = {
                "is_updated": False,
                "is_summary_updated": False,
                "summary": content_item.get("abstract", "") or content_item.get("description", ""),
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
            
            # Include available metadata
            meta_data = {
                "track": content_item.get("track", ""),
                "tags": content_item.get("tags", []),
                "sessionType": content_item.get("sessionType", ""),
                "learningLevel": content_item.get("learningLevel", ""),
                "title": content_item.get("title", ""),
                "sessionId": content_item.get("sessionId", ""),
                "durationMinutes": content_item.get("durationMinutes"),
                "sessionDate": content_item.get("sessionDate"),
                "industry": content_item.get("industry", ""),
            }
            
            # Add any custom metadata from the content item
            if content_item.get("metadata"):
                for key, value in content_item.get("metadata", {}).items():
                    if key not in meta_data and value:
                        meta_data[key] = value
            
            # Add any file-specific metadata
            if file_info.get("type"):
                meta_data["fileType"] = file_info.get("type")
            if file_info.get("name"):
                meta_data["fileName"] = file_info.get("name")
            if file_info.get("size"):
                meta_data["fileSize"] = file_info.get("size")
            
            file_entry["meta_data"] = meta_data
            
            # Add to list if we have required URLs
            if "drive_url" in file_entry or "file_url" in file_entry:
                file_entries.append(file_entry)
        
        # If no file URLs were found in fileUrls array, create a default entry from legacy fields
        if not file_entries:
            # Build default file entry from the content metadata
            default_entry = {
                "is_updated": False,
                "is_summary_updated": False,
                "summary": content_item.get("abstract", "") or content_item.get("description", ""),
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
            
            # Add metadata
            meta_data = {
                "track": content_item.get("track", ""),
                "tags": content_item.get("tags", []),
                "sessionType": content_item.get("sessionType", ""),
                "learningLevel": content_item.get("learningLevel", ""),
                "title": content_item.get("title", ""),
                "sessionId": content_item.get("sessionId", ""),
                "durationMinutes": content_item.get("durationMinutes"),
                "sessionDate": content_item.get("sessionDate"),
                "industry": content_item.get("industry", ""),
            }
            
            # Add any custom metadata from the content item
            if content_item.get("metadata"):
                for key, value in content_item.get("metadata", {}).items():
                    if key not in meta_data and value:
                        meta_data[key] = value
                        
            default_entry["meta_data"] = meta_data
            
            if "drive_url" in default_entry or "file_url" in default_entry:
                file_entries.append(default_entry)
        
        return file_entries

    def generate_payload(self, session_id: Optional[str] = None, limit: int = 100, collection: str = "content") -> Dict[str, Any]:
        """
        Generate the complete index payload.

        Args:
            session_id: Optional session ID (generated if not provided)
            limit: Maximum number of content items to include
            collection: Collection to query for content items

        Returns:
            Complete index payload
        """
        # Generate session ID if not provided
        if not session_id:
            session_id = f"session-{uuid.uuid4()}"
        
        # Get content documents
        content_items = self.get_content_documents(collection, limit)
        
        # Create file list
        file_list = []
        for item in content_items:
            entries = self.create_file_entries(item)
            file_list.extend(entries)
        
        # Create the complete payload
        payload = {
            "session_id": session_id,
            "file_list": file_list
        }
        
        return payload

    def save_payload(self, payload: Dict[str, Any], output_file: str = "index_payload.json"):
        """
        Save the payload to a JSON file.

        Args:
            payload: The index payload
            output_file: Path to output file
        """
        try:
            with open(output_file, 'w') as f:
                json.dump(payload, f, indent=2)
            logger.info(f"Saved payload to {output_file}")
            print(f"Payload saved to {output_file}")
            print(f"Total files in payload: {len(payload['file_list'])}")
        except Exception as e:
            logger.error(f"Error saving payload: {e}")
            print(f"Error saving payload: {e}")

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
            print(f"Payload contains {len(payload['file_list'])} files")
            
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


def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description="Generate index payload from Firestore content")
    parser.add_argument("--credentials", help="Path to service account credentials file")
    parser.add_argument("--collection", default="content", help="Collection name to use")
    parser.add_argument("--session-id", help="Session ID for the indexing batch")
    parser.add_argument("--limit", type=int, default=100, help="Maximum number of documents to process")
    parser.add_argument("--output", default="index_payload.json", help="Output file path")
    parser.add_argument("--endpoint", help="Indexer API endpoint URL")
    
    args = parser.parse_args()
    
    # Initialize the generator with credentials
    generator = IndexPayloadGenerator(credentials_path=args.credentials)
    
    # Generate payload
    print(f"Generating indexing payload from '{args.collection}' collection...")
    payload = generator.generate_payload(
        session_id=args.session_id,
        limit=args.limit,
        collection=args.collection
    )
    
    # Display summary of generated payload
    print(f"Generated payload with session_id: {payload['session_id']}")
    print(f"Total files in payload: {len(payload['file_list'])}")
    
    # Save payload to file
    generator.save_payload(payload, args.output)
    
    # Send to indexer if endpoint provided
    if args.endpoint:
        generator.send_to_indexer(payload, args.endpoint)


if __name__ == "__main__":
    main() 