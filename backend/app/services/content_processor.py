"""
Service for processing content items from bulk uploads.
"""
import os
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import requests
from google.cloud import storage
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from app.core.logging import configure_logging
from app.db.firestore_client import FirestoreClient

# Setup logging
logger = configure_logging()


class ContentProcessor:
    """Service for processing content items from bulk uploads."""

    def __init__(self) -> None:
        """Initialize the content processor."""
        try:
            logger.info("Initializing ContentProcessor")

            # Initialize Firestore client
            try:
                self.firestore = FirestoreClient()
                logger.info("ContentProcessor: Firestore client initialized successfully")
            except Exception as db_error:
                logger.error(
                    f"ContentProcessor: Failed to initialize Firestore client: {str(db_error)}",
                    exc_info=True,
                )
                # Re-raise to fail initialization
                raise

            # Use environment variables with proper defaults for App Engine
            # Temporary dir for file processing
            self.temp_dir = os.environ.get("TEMP_PROCESSING_DIR", "/tmp/processing")
            os.makedirs(self.temp_dir, exist_ok=True)

            # Initialize Storage client for uploading files
            try:
                self.storage_client = storage.Client()
                bucket_name = os.environ.get("GCS_BUCKET_NAME")
                if not bucket_name:
                    logger.warning("GCS_BUCKET_NAME not set, file uploads will fail")
                    self.bucket = None
                else:
                    self.bucket = self.storage_client.bucket(bucket_name)
                    logger.info(f"ContentProcessor: Storage client initialized with bucket {bucket_name}")
            except Exception as storage_error:
                logger.error(
                    f"ContentProcessor: Failed to initialize Storage client: {str(storage_error)}",
                    exc_info=True,
                )
                self.bucket = None

            logger.info("ContentProcessor initialization completed successfully")

        except Exception as e:
            logger.error(f"Critical error initializing ContentProcessor: {str(e)}", exc_info=True)
            # Re-raise to fail initialization
            raise

    def _check_duplicate_session_id(self, session_id: str) -> bool:
        """
        Check if a session ID already exists in Firestore.
        
        Args:
            session_id: The session ID to check
            
        Returns:
            True if duplicate exists, False otherwise
        """
        if not session_id:
            return False
            
        try:
            # Query Firestore for documents with matching sessionId
            filters = [("sessionId", "==", session_id)]
            results = self.firestore.list_documents("content", limit=1, filters=filters)
            
            # If any results found, this is a duplicate
            return len(results) > 0
        except Exception as e:
            logger.error(f"Error checking for duplicate session ID: {str(e)}")
            # In case of error, assume it's not a duplicate to allow the upload to proceed
            return False

    async def process_slides_from_drive(
        self, content_id: str, drive_url: str
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Process slides from Google Drive URL or folder link.
        This handles:
        1. Direct links to presentations
        2. Folder links that contain presentations
        
        Args:
            content_id: ID of the content
            drive_url: Google Drive URL (file or folder)
            
        Returns:
            Tuple of (success, message, slides_info)
        """
        try:
            # Extract Drive ID from URL
            drive_id = self._extract_drive_id(drive_url)
            if not drive_id:
                return False, "Invalid Google Drive URL", None
                
            # Build Drive service
            try:
                # Check if a service account file path is specified
                service_account_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_PATH")
                
                if service_account_path and os.path.exists(service_account_path):
                    # Use the service account file if provided
                    from google.oauth2 import service_account
                    credentials = service_account.Credentials.from_service_account_file(
                        service_account_path,
                        scopes=["https://www.googleapis.com/auth/drive.readonly"]
                    )
                    drive_service = build("drive", "v3", credentials=credentials, cache_discovery=False)
                    logger.info("Successfully created Drive service with service account credentials")
                else:
                    # Fall back to default credentials
                    drive_service = build("drive", "v3", cache_discovery=False)
                    logger.info("Successfully created Drive service with default credentials")
            except Exception as auth_error:
                logger.error(f"Failed to authenticate with Google Drive: {str(auth_error)}")
                return False, f"Drive authentication failed: {str(auth_error)}", None
                
            # Get file metadata
            try:
                file = drive_service.files().get(
                    fileId=drive_id,
                    fields="id,name,mimeType,size,webViewLink,thumbnailLink,iconLink",
                    supportsAllDrives=True
                ).execute()
            except Exception as meta_error:
                logger.error(f"Failed to get Drive file metadata: {str(meta_error)}")
                return False, f"Failed to access Drive file: {str(meta_error)}", None
                
            # If it's a folder, find presentation files
            presentation_files = []
            if file.get("mimeType") == "application/vnd.google-apps.folder":
                logger.info(f"Processing folder: {drive_id}")
                try:
                    # List all files in the folder
                    results = drive_service.files().list(
                        q=f"'{drive_id}' in parents",
                        fields="files(id,name,mimeType,size,webViewLink,thumbnailLink,iconLink)",
                        pageSize=10,  # Limit to 10 files
                        supportsAllDrives=True,
                        includeItemsFromAllDrives=True
                    ).execute()
                    
                    folder_files = results.get("files", [])
                    if not folder_files:
                        return False, "Drive folder is empty", None
                        
                    # Filter for presentation files
                    for folder_file in folder_files:
                        mime_type = folder_file.get("mimeType", "")
                        if (mime_type == "application/vnd.google-apps.presentation" or
                            "presentation" in mime_type.lower() or
                            folder_file.get("name", "").lower().endswith((".ppt", ".pptx"))):
                            presentation_files.append(folder_file)
                            
                    if not presentation_files:
                        return False, "No presentation files found in folder", None
                        
                    # Sort by filename - look for "presentation" or "deck" in the name first
                    def score_presentation(f):
                        name = f.get("name", "").lower()
                        if "presentation" in name: return 0
                        if "deck" in name: return 1
                        if "slides" in name: return 2
                        if "recap" in name: return 3
                        return 100
                        
                    presentation_files.sort(key=score_presentation)
                    
                    # Find presentation slides and recap slides if possible
                    presentation_file = None
                    recap_file = None
                    
                    for pres in presentation_files:
                        name = pres.get("name", "").lower()
                        if "recap" in name:
                            if not recap_file:
                                recap_file = pres
                        else:
                            if not presentation_file:
                                presentation_file = pres
                    
                    # If we still don't have a presentation, use the first available
                    if not presentation_file and presentation_files:
                        presentation_file = presentation_files[0]
                        
                    # Process each file (presentation and recap if available)
                    results = []
                    if presentation_file:
                        success, message, file_info = await self._process_file_from_drive(
                            content_id, presentation_file.get("id")
                        )
                        if success and file_info:
                            file_info["presentation_type"] = "presentation_slides"
                            results.append(file_info)
                            
                    if recap_file:
                        success, message, file_info = await self._process_file_from_drive(
                            content_id, recap_file.get("id")
                        )
                        if success and file_info:
                            file_info["presentation_type"] = "recap_slides"
                            results.append(file_info)
                            
                    if not results:
                        return False, "Failed to process presentation files", None
                        
                    # Return combined results
                    return True, "Presentation files processed successfully", results
                        
                except Exception as folder_error:
                    logger.error(f"Failed to process Drive folder: {str(folder_error)}")
                    return False, f"Failed to process Drive folder: {str(folder_error)}", None
            
            # Process single presentation file
            else:
                # Check if it's a presentation
                mime_type = file.get("mimeType", "")
                if (mime_type != "application/vnd.google-apps.presentation" and
                    "presentation" not in mime_type.lower() and
                    not file.get("name", "").lower().endswith((".ppt", ".pptx"))):
                    logger.warning(f"File is not a presentation: {mime_type}")
                    # Still try to process it anyway
                
                # Determine if this is likely a recap or main presentation
                presentation_type = "presentation_slides"
                if "recap" in file.get("name", "").lower():
                    presentation_type = "recap_slides"
                    
                # Process the file
                success, message, file_info = await self._process_file_from_drive(
                    content_id, drive_id
                )
                
                if success and file_info:
                    file_info["presentation_type"] = presentation_type
                    return True, "Presentation file processed successfully", [file_info]
                else:
                    return False, message, None
                    
        except Exception as e:
            logger.error(f"Error processing slides from Drive: {str(e)}")
            return False, f"Error processing slides: {str(e)}", None
            
    async def process_content_item(
        self,
        content_data: Dict[str, Any],
        file_url: Optional[str] = None,
        drive_file_id: Optional[str] = None,
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Process a single content item from a batch upload.

        Args:
            content_data: Content metadata.
            file_url: Optional URL to a file.
            drive_file_id: Optional Google Drive file ID.

        Returns:
            Tuple of (success, message, content_item).
        """
        try:
            # Generate a content ID
            content_id = self.firestore.generate_id()

            # Set created and updated timestamps
            now = datetime.now().isoformat()
            content_data["createdAt"] = now
            content_data["updatedAt"] = now

            # Check for sessionId duplication
            session_id = content_data.get("sessionId")
            if session_id and self._check_duplicate_session_id(session_id):
                logger.warning(f"Duplicate session ID found: {session_id}")
                return False, f"Duplicate session ID found: {session_id}", None

            # Ensure we have a fileUrls array
            if "fileUrls" not in content_data:
                content_data["fileUrls"] = []
            
            logger.info(f"Starting processing for content item: {content_id}")
            
            # Track which types we've already processed
            processed_types = set()

            # Check for slide URLs (presentation/recap)
            presentation_slides_url = content_data.get("presentationSlidesUrl")
            recap_slides_url = content_data.get("recapSlidesUrl")
            
            # Helper function to find existing entry by presentation_type
            def find_existing_entry(file_urls, ptype):
                for i, entry in enumerate(file_urls):
                    if entry.get("presentation_type") == ptype:
                        return i, entry
                return -1, None
            
            # Helper function to update or add entry
            def update_or_add_entry(file_urls, new_entry, ptype):
                idx, existing = find_existing_entry(file_urls, ptype)
                if idx >= 0:
                    # Update existing entry
                    logger.info(f"Updating existing {ptype} entry with processed data")
                    file_urls[idx].update(new_entry)
                    return file_urls[idx]
                else:
                    # Add new entry
                    logger.info(f"Adding new {ptype} entry")
                    file_urls.append(new_entry)
                    return new_entry
            
            # Process presentation slides if a Google Drive URL is provided
            if presentation_slides_url and self._extract_drive_id(presentation_slides_url):
                logger.info(f"Processing presentation slides URL: {presentation_slides_url}")
                success, message, slides_info = await self.process_slides_from_drive(
                    content_id, presentation_slides_url
                )
                if success and slides_info:
                    # For each slide deck processed
                    for slide_info in slides_info:
                        if slide_info.get("presentation_type") == "presentation_slides":
                            # Add to processed types
                            processed_types.add("presentation_slides")
                            # Set URL and update fileUrls
                            content_data["presentationSlidesUrl"] = str(slide_info["url"])
                            logger.info(f"Set presentationSlidesUrl to: {slide_info['url']}")
                            # Ensure correct type values
                            slide_info["contentType"] = "presentation"
                            # Update or add to fileUrls
                            update_or_add_entry(content_data["fileUrls"], slide_info, "presentation_slides")
                else:
                    logger.warning(f"Failed to process presentation slides: {message}")
            
            # Process the recap slides from recapSlidesUrl if it exists
            if recap_slides_url and recap_slides_url != presentation_slides_url and self._extract_drive_id(recap_slides_url):
                logger.info(f"Processing recap slides URL: {recap_slides_url}")
                success, message, slides_info = await self.process_slides_from_drive(
                    content_id, recap_slides_url
                )
                if success and slides_info:
                    # For each slide deck processed
                    for slide_info in slides_info:
                        if slide_info.get("presentation_type") == "recap_slides":
                            # Add to processed types
                            processed_types.add("recap_slides")
                            # Set URL and update fileUrls
                            content_data["recapSlidesUrl"] = str(slide_info["url"])
                            logger.info(f"Set recapSlidesUrl to: {slide_info['url']}")
                            # Ensure correct type values
                            slide_info["contentType"] = "presentation"
                            # Update or add to fileUrls
                            update_or_add_entry(content_data["fileUrls"], slide_info, "recap_slides")
                else:
                    logger.warning(f"Failed to process recap slides: {message}")
            
            # Process driveLink if provided - could be a folder containing slide decks
            # Check both "driveLink" and "drive_link" for maximum compatibility
            drive_link = content_data.get("driveLink") or content_data.get("drive_link")
            if drive_link and self._extract_drive_id(drive_link) and not drive_file_id and "drive_folder" not in processed_types:
                # Only process drive_link if drive_file_id isn't already specified
                logger.info(f"Processing drive link: {drive_link}")
                
                # Create a simple folder entry
                folder_info = {
                    "contentType": "folder",
                    "presentation_type": "drive_folder",
                    "name": "Drive Folder",
                    "source": "drive",
                    "drive_url": drive_link,
                    "driveId": self._extract_drive_id(drive_link),
                    "gcs_path": None, # Folders don't have gcs_path
                    "url": drive_link
                }
                
                # Add to processed types
                processed_types.add("drive_folder")
                
                # Update or add to fileUrls
                update_or_add_entry(content_data["fileUrls"], folder_info, "drive_folder")
                logger.info(f"Added drive folder: {drive_link}")
            
            # Process YouTube URL if provided
            youtube_url = content_data.get("videoYoutubeUrl")
            if youtube_url and "youtube_video" not in processed_types:
                youtube_id = self._extract_youtube_id(youtube_url)
                if youtube_id:
                    # Create YouTube entry
                    youtube_info = {
                        "contentType": "video",
                        "presentation_type": "youtube_video",
                        "name": content_data.get("ytVideoTitle") or "YouTube Video",
                        "source": "youtube",
                        "drive_url": youtube_url,
                        "gcs_path": None, # YouTube videos don't have gcs_path
                        "url": youtube_url
                    }
                    
                    # Add to processed types
                    processed_types.add("youtube_video")
                    
                    # Update or add to fileUrls
                    update_or_add_entry(content_data["fileUrls"], youtube_info, "youtube_video")
                    logger.info(f"Added YouTube video: {youtube_url}")
            
            # Continue with regular processing for Drive file ID or file URL
            if drive_file_id:
                success, message, file_info = await self._process_file_from_drive(
                    content_id, drive_file_id
                )
                if success and file_info:
                    # Set presentation_type if not already set
                    if "presentation_type" not in file_info:
                        mime_type = file_info.get("type", "")
                        if "presentation" in mime_type:
                            file_info["presentation_type"] = "presentation_slides"
                        elif "folder" in mime_type:
                            file_info["presentation_type"] = "drive_folder"
                    
                    # Only add if it's one of our 4 standard types and we haven't already processed this type
                    ptype = file_info.get("presentation_type")
                    if ptype in ["presentation_slides", "recap_slides", "drive_folder", "youtube_video"] and ptype not in processed_types:
                        # Update or add to fileUrls
                        update_or_add_entry(content_data["fileUrls"], file_info, ptype)
                        processed_types.add(ptype)
                        
                        # Set drive fields according to content model
                        content_data["drive_id"] = drive_file_id
                        content_data["drive_link"] = file_info.get("webViewLink", "")

                        # Set proper URL fields based on file type
                        if ptype == "presentation_slides":
                            content_data["presentationSlidesUrl"] = file_info["url"]
                        elif ptype == "recap_slides":
                            content_data["recapSlidesUrl"] = file_info["url"]

            # Process file URL if provided
            if file_url:
                # Check if it's a YouTube video
                youtube_id = self._extract_youtube_id(file_url)
                if youtube_id and "youtube_video" not in processed_types:
                    # Process as YouTube video
                    content_data["videoYoutubeUrl"] = file_url
                    
                    # Add to fileUrls for consistency
                    youtube_info = {
                        "url": file_url,
                        "name": content_data.get("ytVideoTitle") or "YouTube Video",
                        "type": "video/youtube",
                        "contentType": "video",
                        "presentation_type": "youtube_video",
                        "source": "youtube",
                        "gcs_path": None # YouTube videos don't have gcs_path
                    }
                    content_data["fileUrls"].append(youtube_info)
                    processed_types.add("youtube_video")

                # Check if it's a Drive URL
                else:
                    drive_id = self._extract_drive_id(file_url)

                    if drive_id:
                        # Process file via Drive API
                        success, message, file_info = await self._process_file_from_drive(
                            content_id, drive_id
                        )
                        if success and file_info:
                            # Set presentation_type if not already set
                            if "presentation_type" not in file_info:
                                mime_type = file_info.get("type", "")
                                if "presentation" in mime_type:
                                    file_info["presentation_type"] = "presentation_slides"
                                elif "folder" in mime_type:
                                    file_info["presentation_type"] = "drive_folder"
                            
                            # Only add if it's one of our 4 standard types and we haven't already processed this type
                            ptype = file_info.get("presentation_type")
                            if ptype in ["presentation_slides", "recap_slides", "drive_folder", "youtube_video"] and ptype not in processed_types:
                                # Update or add to fileUrls
                                update_or_add_entry(content_data["fileUrls"], file_info, ptype)
                                processed_types.add(ptype)
                                
                                # Set drive fields according to content model
                                content_data["drive_id"] = drive_id
                                content_data["drive_link"] = file_url

                                # Set proper URL fields based on file type
                                if ptype == "presentation_slides":
                                    content_data["presentationSlidesUrl"] = file_info["url"]
                                elif ptype == "recap_slides":
                                    content_data["recapSlidesUrl"] = file_info["url"]

                    elif file_url.startswith(("http://", "https://", "ftp://")):
                        # Process regular URL
                        success, message, file_info = await self._process_file_from_url(
                            content_id, file_url
                        )
                        if success and file_info:
                            # Set presentation_type if not already set
                            if "presentation_type" not in file_info:
                                mime_type = file_info.get("type", "")
                                if "presentation" in mime_type:
                                    file_info["presentation_type"] = "presentation_slides"
                            
                            # Only add if it's one of our 4 standard types and we haven't already processed this type
                            ptype = file_info.get("presentation_type")
                            if ptype in ["presentation_slides", "recap_slides", "drive_folder", "youtube_video"] and ptype not in processed_types:
                                # Update or add to fileUrls
                                update_or_add_entry(content_data["fileUrls"], file_info, ptype)
                                processed_types.add(ptype)
                                content_data["file_path"] = file_info["url"]

            # Ensure we only have our 4 specified file types
            standardized_file_urls = []
            for entry in content_data["fileUrls"]:
                ptype = entry.get("presentation_type")
                if ptype in ["presentation_slides", "recap_slides", "drive_folder", "youtube_video"]:
                    # Create a clean entry with all necessary fields
                    clean_entry = {
                        "contentType": entry.get("contentType", "unknown"),
                        "presentation_type": ptype,
                        "name": entry.get("name", ""),
                        "source": entry.get("source", ""),
                        "drive_url": entry.get("drive_url", ""),
                        "driveId": entry.get("driveId", ""),
                        "gcs_path": entry.get("gcs_path"),
                        "url": entry.get("url"),
                        "type": entry.get("type", ""),
                        "size": entry.get("size", 0),
                        "thumbnailLink": entry.get("thumbnailLink"),
                    }
                    
                    # Add exportUrl if available - important for large files that can't be exported directly
                    if entry.get("exportUrl"):
                        clean_entry["exportUrl"] = entry.get("exportUrl")
                    
                    # Ensure content type is set correctly
                    if not clean_entry["contentType"] or clean_entry["contentType"] == "unknown":
                        if ptype in ["presentation_slides", "recap_slides"]:
                            clean_entry["contentType"] = "presentation"
                        elif ptype == "youtube_video":
                            clean_entry["contentType"] = "video"
                        elif ptype == "drive_folder":
                            clean_entry["contentType"] = "folder"
                    
                    # Ensure name is set
                    if not clean_entry["name"]:
                        if ptype == "presentation_slides":
                            clean_entry["name"] = "Presentation Slides"
                        elif ptype == "recap_slides":
                            clean_entry["name"] = "Recap Slides"
                        elif ptype == "drive_folder":
                            clean_entry["name"] = "Drive Folder"
                        elif ptype == "youtube_video":
                            clean_entry["name"] = "YouTube Video"
                    
                    # Ensure source is set
                    if not clean_entry["source"]:
                        if ptype in ["presentation_slides", "recap_slides", "drive_folder"]:
                            clean_entry["source"] = "drive"
                        elif ptype == "youtube_video":
                            clean_entry["source"] = "youtube"
                            
                    # Use URL as drive_url if drive_url is missing but URL exists
                    if not clean_entry["drive_url"] and clean_entry["url"]:
                        clean_entry["drive_url"] = clean_entry["url"]
                    
                    # Use drive_url as URL if URL is missing but drive_url exists
                    if not clean_entry["url"] and clean_entry["drive_url"]:
                        clean_entry["url"] = clean_entry["drive_url"]
                    
                    # Use exportUrl as URL if URL is missing but exportUrl exists
                    if not clean_entry["url"] and clean_entry.get("exportUrl"):
                        clean_entry["url"] = clean_entry["exportUrl"]
                    
                    standardized_file_urls.append(clean_entry)
            
            # Replace fileUrls with standardized version
            content_data["fileUrls"] = standardized_file_urls

            # Ensure tags field exists
            if "tags" not in content_data:
                content_data["tags"] = []

            # Ensure metadata field exists
            if "metadata" not in content_data:
                content_data["metadata"] = {}

            # Set used flag if not present
            if "used" not in content_data:
                content_data["used"] = False

            # Store in Firestore
            success = self.firestore.create_document("content", content_id, content_data)
            if not success:
                return False, "Failed to store content metadata", None

            # Store the content_id in the content_data dictionary so it's available to callers
            content_data["id"] = content_id

            # Log stored data for debugging purposes
            logger.info(f"Content created with ID: {content_id}")
            
            # Log the fileUrls entries for verification
            for i, entry in enumerate(content_data.get("fileUrls", [])):
                logger.info(f"Content {content_id} fileUrl {i}: type={entry.get('presentation_type')}, gcs_path={entry.get('gcs_path')}")
                
            if "recapSlidesUrl" in content_data:
                logger.info(f"recapSlidesUrl stored: {content_data.get('recapSlidesUrl')}")
            else:
                logger.warning(f"recapSlidesUrl not present in content_data for content ID: {content_id}")

            return True, "Content created successfully", content_data

        except Exception as e:
            logger.error(f"Error processing content item: {str(e)}")
            return False, f"Error processing content: {str(e)}", None

    def _extract_drive_id(self, url_or_id: str) -> Optional[str]:
        """
        Extract Google Drive file ID from URL or return the ID if already an ID.

        Handles various Drive URL formats:
        - https://drive.google.com/file/d/{fileId}/view
        - https://drive.google.com/open?id={fileId}
        - https://docs.google.com/document/d/{fileId}/edit
        - https://docs.google.com/presentation/d/{fileId}/edit
        - etc.

        Returns None if not a Drive URL/ID.
        """
        # If it's a YouTube link, return None to handle it separately
        if "youtube.com" in url_or_id or "youtu.be" in url_or_id:
            return None
            
        # If empty or None, return None
        if not url_or_id:
            return None

        # If it's a short string with no slashes, might be a direct file ID
        if len(url_or_id) >= 25 and len(url_or_id) <= 44 and "/" not in url_or_id:
            return url_or_id

        # Common Drive URL patterns
        file_id_patterns = [
            r"drive\.google\.com/file/d/([^/]+)",
            r"drive\.google\.com/open\?id=([^&]+)",
            r"docs\.google\.com/\w+/d/([^/]+)",
            r"docs\.google\.com/presentation/d/([^/]+)",
            r"docs\.google\.com/document/d/([^/]+)",
            r"docs\.google\.com/spreadsheets/d/([^/]+)",
            r"drive\.google\.com/drive/folders/([^?&/]+)",
        ]

        for pattern in file_id_patterns:
            match = re.search(pattern, url_or_id)
            if match:
                # Extract ID and remove any trailing characters (like /edit#slide=id.xxx)
                drive_id = match.group(1)
                # If the ID contains a hash or question mark, trim it
                if '#' in drive_id:
                    drive_id = drive_id.split('#')[0]
                if '?' in drive_id:
                    drive_id = drive_id.split('?')[0]
                return drive_id

        return None

    def _extract_youtube_id(self, url: str) -> Optional[str]:
        """
        Extract YouTube video ID from various YouTube URL formats.

        Returns None if not a valid YouTube URL.
        """
        youtube_patterns = [
            r"youtube\.com/watch\?v=([^&]+)",
            r"youtu\.be/([^?&/]+)",
            r"youtube\.com/embed/([^?&/]+)",
            r"youtube\.com/v/([^?&/]+)",
        ]

        for pattern in youtube_patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    async def _process_file_from_drive(
        self, content_id: str, file_id: str
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Download and process a file from Google Drive.

        Args:
            content_id: ID of the content.
            file_id: Google Drive file ID.

        Returns:
            Tuple of (success, message, file_info).
        """
        temp_file_path = None

        try:
            # Build the Drive service using App Engine default credentials or service account
            try:
                # Check if a service account file path is specified
                service_account_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_PATH")
                
                if service_account_path and os.path.exists(service_account_path):
                    # Use the service account file if provided
                    from google.oauth2 import service_account
                    credentials = service_account.Credentials.from_service_account_file(
                        service_account_path,
                        scopes=["https://www.googleapis.com/auth/drive.readonly"]
                    )
                    drive_service = build("drive", "v3", credentials=credentials, cache_discovery=False)
                    logger.info("Successfully created Drive service with service account credentials")
                else:
                    # Fall back to default credentials
                    drive_service = build("drive", "v3", cache_discovery=False)
                    logger.info("Successfully created Drive service with default credentials")
            except Exception as auth_error:
                logger.error(f"Failed to authenticate with Google Drive: {str(auth_error)}")
                return False, f"Drive authentication failed: {str(auth_error)}", None

            # Get file metadata with more fields including webViewLink
            try:
                file = (
                    drive_service.files()
                    .get(
                        fileId=file_id,
                        fields="id,name,mimeType,size,webViewLink,thumbnailLink,iconLink",
                        supportsAllDrives=True,
                    )
                    .execute()
                )
            except Exception as meta_error:
                logger.error(f"Failed to get Drive file metadata: {str(meta_error)}")
                return False, f"Failed to access Drive file: {str(meta_error)}", None

            # Check if it's a folder
            if file.get("mimeType") == "application/vnd.google-apps.folder":
                try:
                    # Handle folder by listing files and selecting first file
                    results = (
                        drive_service.files()
                        .list(
                            q=f"'{file_id}' in parents",
                            fields="files(id,name,mimeType,size,webViewLink,thumbnailLink,iconLink)",
                            pageSize=1,  # Just get the first file
                            supportsAllDrives=True,
                            includeItemsFromAllDrives=True,
                        )
                        .execute()
                    )
                    folder_files = results.get("files", [])

                    if not folder_files:
                        return False, "Drive folder is empty", None

                    # Use the first file
                    file_id = folder_files[0]["id"]
                    # Get updated metadata for the specific file
                    file = (
                        drive_service.files()
                        .get(
                            fileId=file_id,
                            fields="id,name,mimeType,size,webViewLink,thumbnailLink,iconLink",
                            supportsAllDrives=True,
                        )
                        .execute()
                    )
                except Exception as folder_error:
                    logger.error(f"Failed to process Drive folder: {str(folder_error)}")
                    return False, f"Failed to process Drive folder: {str(folder_error)}", None

            # Create temp file path
            file_name = file.get("name", f"file_{uuid.uuid4()}")
            temp_file_name = f"{uuid.uuid4()}_{file_name}"
            temp_file_path = os.path.join(self.temp_dir, temp_file_name)

            # Map content types to more standardized types for the content model
            content_type_map = {
                "application/vnd.google-apps.document": "document",
                "application/vnd.google-apps.spreadsheet": "spreadsheet",
                "application/vnd.google-apps.presentation": "presentation",
                "application/pdf": "document",
                "application/vnd.openxmlformats-officedocument.presentationml.presentation": "presentation",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "document",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "spreadsheet",
                "video/mp4": "video",
                "video/quicktime": "video",
                "video/mpeg": "video",
                "video/webm": "video",
                "audio/mpeg": "audio",
                "audio/mp4": "audio",
                "image/jpeg": "image",
                "image/png": "image",
                "image/gif": "image",
            }

            # Handle Google Workspace files (Docs, Sheets, Slides)
            mime_type = file.get("mimeType", "")
            # Get standardized content type or use the original if not mapped
            content_type_category = content_type_map.get(mime_type, "unknown")

            if mime_type.startswith("application/vnd.google-apps."):
                try:
                    if "document" in mime_type:
                        # Export as PDF
                        request = drive_service.files().export_media(
                            fileId=file_id, mimeType="application/pdf"
                        )
                        file_extension = ".pdf"
                        export_mime_type = "application/pdf"
                    elif "spreadsheet" in mime_type:
                        # Export as Excel
                        request = drive_service.files().export_media(
                            fileId=file_id,
                            mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                        file_extension = ".xlsx"
                        export_mime_type = (
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    elif "presentation" in mime_type:
                        # Export as PowerPoint
                        request = drive_service.files().export_media(
                            fileId=file_id,
                            mimeType="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                        )
                        file_extension = ".pptx"
                        export_mime_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
                    else:
                        # Default to PDF for other Google formats
                        request = drive_service.files().export_media(
                            fileId=file_id, mimeType="application/pdf"
                        )
                        file_extension = ".pdf"
                        export_mime_type = "application/pdf"

                    # Make sure filename has the right extension
                    if not file_name.lower().endswith(file_extension):
                        file_name = f"{os.path.splitext(file_name)[0]}{file_extension}"
                        temp_file_name = f"{uuid.uuid4()}_{file_name}"
                        temp_file_path = os.path.join(self.temp_dir, temp_file_name)

                    # Use the export MIME type
                    mime_type = export_mime_type

                except Exception as export_error:
                    logger.error(f"Failed to export Google Workspace file: {str(export_error)}")
                    return (
                        False,
                        f"Failed to export Google Workspace file: {str(export_error)}",
                        None,
                    )
            else:
                # Regular file
                try:
                    request = drive_service.files().get_media(fileId=file_id, supportsAllDrives=True)
                except Exception as get_error:
                    logger.error(f"Failed to get Drive file: {str(get_error)}")
                    return False, f"Failed to access Drive file: {str(get_error)}", None

            # Download file content
            try:
                # For large files, use a chunked download approach
                CHUNK_SIZE = 1024 * 1024 * 5  # 5MB chunks
                file_size = int(file.get("size", 0))
                
                # If file is very large (over 100MB), use a different approach
                if file_size > 100 * 1024 * 1024:  # 100MB
                    logger.warning(f"File is very large ({file_size} bytes), using webViewLink instead")
                    # Return a special file info that just contains the link
                    file_info = {
                        "url": file.get("webViewLink", ""),
                        "name": file.get("name", f"file_{uuid.uuid4()}"),
                        "type": mime_type,
                        "contentType": content_type_category,
                        "size": file_size,
                        "driveId": file_id,
                        "webViewLink": file.get("webViewLink", ""),
                        "thumbnailLink": file.get("thumbnailLink", ""),
                        "iconLink": file.get("iconLink", ""),
                        "source": "drive",
                        "tooLargeToDownload": True
                    }
                    return True, "File link saved (too large to download)", file_info
                
                # Standard download with improved chunking and retry logic
                with open(temp_file_path, "wb") as f:
                    downloader = MediaIoBaseDownload(f, request, chunksize=CHUNK_SIZE)
                    done = False
                    retry_count = 0
                    max_retries = 5  # Increased retries for large files
                    backoff_time = 1  # Starting backoff in seconds

                    while not done and retry_count < max_retries:
                        try:
                            status, done = downloader.next_chunk()
                            # Log progress for large files
                            if file_size > 10 * 1024 * 1024:  # 10MB
                                if status:
                                    logger.info(f"Downloaded {int(status.progress() * 100)}% of file {file_id}")
                            # Reset backoff on successful chunk
                            backoff_time = 1
                        except Exception as chunk_error:
                            error_str = str(chunk_error)
                            logger.warning(
                                f"Error downloading chunk, attempt {retry_count+1}: {error_str}"
                            )
                            
                            # For export size limits, break immediately and use fallback
                            if "exportSizeLimitExceeded" in error_str or "This file is too large to be exported" in error_str:
                                raise chunk_error
                                
                            # For rate limits or temporary issues, use exponential backoff
                            import time
                            time.sleep(backoff_time)
                            backoff_time *= 2  # Exponential backoff
                            retry_count += 1
                            
                            if retry_count >= max_retries:
                                raise chunk_error
            except Exception as download_error:
                logger.error(f"Failed to download Drive file: {str(download_error)}")
                
                # Check if this is an export size limit error
                error_str = str(download_error)
                if "exportSizeLimitExceeded" in error_str or "This file is too large to be exported" in error_str:
                    logger.info(f"File is too large to export in requested format, using direct link")
                    
                    # Get additional metadata if we don't have it already
                    try:
                        detailed_file = drive_service.files().get(
                            fileId=file_id, 
                            fields="id,name,mimeType,size,webViewLink,webContentLink,exportLinks,thumbnailLink,iconLink"
                        ).execute()
                        
                        # For Google Workspace files, use the exportLinks when available
                        if "exportLinks" in detailed_file and detailed_file.get("exportLinks"):
                            # Get available export formats
                            export_links = detailed_file.get("exportLinks", {})
                            logger.info(f"Available export formats: {list(export_links.keys())}")
                            
                            # Prioritize PDF format for presentations and documents
                            export_url = None
                            mime_type = "application/link"  # Default fallback
                            
                            if "application/pdf" in export_links:
                                export_url = export_links["application/pdf"]
                                mime_type = "application/pdf"
                            # Try other common formats if PDF not available
                            elif "application/vnd.openxmlformats-officedocument.presentationml.presentation" in export_links:
                                export_url = export_links["application/vnd.openxmlformats-officedocument.presentationml.presentation"]
                                mime_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
                            elif "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in export_links:
                                export_url = export_links["application/vnd.openxmlformats-officedocument.wordprocessingml.document"]  
                                mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            
                            # If we found an export URL, use it
                            if export_url:
                                logger.info(f"Using export link for {mime_type} instead")
                                
                                # Also generate a direct export URL for presentations
                                direct_export_url = None
                                if "presentation" in mime_type.lower():
                                    direct_export_url = f"https://docs.google.com/presentation/d/{file_id}/export/pptx"
                                    logger.info(f"Generated direct export URL: {direct_export_url}")
                                
                                # Create a special file info with the export link
                                file_info = {
                                    "url": export_url,
                                    "name": detailed_file.get("name", f"file_{uuid.uuid4()}"),
                                    "type": mime_type,
                                    "contentType": content_type_category,
                                    "size": 0,  # Size unknown for export
                                    "driveId": file_id,
                                    "webViewLink": detailed_file.get("webViewLink", ""),
                                    "thumbnailLink": detailed_file.get("thumbnailLink", ""),
                                    "iconLink": detailed_file.get("iconLink", ""),
                                    "source": "drive",
                                    "gcs_path": None,  # No GCS path since we're using the direct URL
                                    "exportUrl": direct_export_url or export_url,
                                    "tooLargeToExport": True  # Set the flag for large files
                                }
                                
                                return True, f"Using direct export link for file (too large to export through API)", file_info
                        
                        # Generate direct export URL for presentations even if no exportLinks available
                        if "presentation" in detailed_file.get("mimeType", "").lower():
                            direct_export_url = f"https://docs.google.com/presentation/d/{file_id}/export/pptx"
                            logger.info(f"Generated direct export URL for presentation: {direct_export_url}")
                            
                            # If no export links or not a Google Workspace file, use webViewLink and direct export URL
                            file_info = {
                                "url": detailed_file.get("webViewLink", ""),
                                "name": detailed_file.get("name", f"file_{uuid.uuid4()}"),
                                "type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                                "contentType": "presentation",
                                "size": 0,
                                "driveId": file_id,
                                "webViewLink": detailed_file.get("webViewLink", ""),
                                "thumbnailLink": detailed_file.get("thumbnailLink", ""),
                                "iconLink": detailed_file.get("iconLink", ""),
                                "source": "drive",
                                "gcs_path": None,  # No GCS path for web links
                                "exportUrl": direct_export_url,
                                "tooLargeToExport": True  # Set the flag for large files
                            }
                            
                            return True, "File link saved (too large to export)", file_info
                        
                    except Exception as detail_error:
                        logger.error(f"Failed to get detailed file info: {str(detail_error)}")
                        
                        # If the file appears to be a presentation based on the error or our knowledge, generate direct export URL
                        if "presentation" in error_str.lower() or mime_type.lower() == "application/vnd.google-apps.presentation":
                            direct_export_url = f"https://docs.google.com/presentation/d/{file_id}/export/pptx"
                            logger.info(f"Generated direct export URL as fallback: {direct_export_url}")
                            
                            # Create minimal file info with direct export URL
                            file_info = {
                                "url": f"https://docs.google.com/presentation/d/{file_id}/edit",
                                "name": file.get("name", f"file_{uuid.uuid4()}"),
                                "type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                                "contentType": "presentation",
                                "size": 0,
                                "driveId": file_id,
                                "webViewLink": file.get("webViewLink", ""),
                                "thumbnailLink": file.get("thumbnailLink", ""),
                                "iconLink": file.get("iconLink", ""),
                                "source": "drive",
                                "gcs_path": None,
                                "exportUrl": direct_export_url,
                                "tooLargeToExport": True  # Set the flag for large files
                            }
                            
                            return True, "File link saved with direct export URL fallback", file_info
                    
                    # If we get here, all export attempts have failed, use webViewLink
                    logger.info(f"All export attempts failed, using webViewLink instead")
                    
                    # For Google Presentations, always generate a direct export URL
                    direct_export_url = None
                    if mime_type.lower() == "application/vnd.google-apps.presentation":
                        direct_export_url = f"https://docs.google.com/presentation/d/{file_id}/export/pptx"
                        logger.info(f"Generated direct export URL as final fallback: {direct_export_url}")
                    
                    # Return a special file info that just contains the link
                    file_info = {
                        "url": file.get("webViewLink", ""),
                        "name": file.get("name", f"file_{uuid.uuid4()}"),
                        "type": "application/link",
                        "contentType": "link",
                        "size": 0,
                        "driveId": file_id,
                        "webViewLink": file.get("webViewLink", ""),
                        "thumbnailLink": file.get("thumbnailLink", ""),
                        "iconLink": file.get("iconLink", ""),
                        "source": "drive",
                        "gcs_path": None, # No GCS path for web links
                        "exportUrl": direct_export_url,
                        "tooLargeToExport": True
                    }
                    
                    # Clean up the temp file if it exists
                    if temp_file_path and os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
                        
                    return True, "File link saved (too large to export)", file_info

            except Exception as e:
                logger.error(f"Failed to process Drive file {file_id}: {str(e)}")
                # Clean up temp file if it exists
                if temp_file_path and os.path.exists(temp_file_path):
                    try:
                        os.remove(temp_file_path)
                    except Exception:
                        pass
                return False, f"Failed to process Drive file: {str(e)}", None

        except Exception as e:
            logger.error(f"Failed to process Drive file {file_id}: {str(e)}")
            # Clean up temp file if it exists
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except Exception:
                    pass
            return False, f"Failed to process Drive file: {str(e)}", None

    async def _process_file_from_url(
        self, content_id: str, file_url: str
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Download and process a file from a URL.

        Args:
            content_id: ID of the content.
            file_url: URL to download file from.

        Returns:
            Tuple of (success, message, file_info).
        """
        temp_file_path = None
        try:
            # Get file name from URL or generate one
            file_name = os.path.basename(file_url.split("?")[0])
            if not file_name:
                file_name = f"file_{uuid.uuid4()}"

            # Create temp file path with unique name to avoid collisions
            temp_file_name = f"{uuid.uuid4()}_{file_name}"
            temp_file_path = os.path.join(self.temp_dir, temp_file_name)

            # Download file with timeout and error handling
            try:
                response = requests.get(file_url, stream=True, timeout=30)
                response.raise_for_status()  # Raise exception for 4XX/5XX responses
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to download file from {file_url}: {str(e)}")
                return False, f"Failed to download file: {str(e)}", None

            with open(temp_file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # Filter out keep-alive chunks
                        f.write(chunk)

            # Check if file was actually downloaded (empty files are suspicious)
            file_size = os.path.getsize(temp_file_path)
            if file_size == 0:
                os.remove(temp_file_path)
                return False, "Downloaded file is empty", None

            # Determine content type (or use a generic one)
            content_type = response.headers.get("Content-Type", "application/octet-stream")

            # Generate a unique file name for storage
            file_extension = os.path.splitext(file_name)[1]
            if not file_extension:
                # Try to guess extension from content type
                if "pdf" in content_type.lower():
                    file_extension = ".pdf"
                elif "powerpoint" in content_type.lower() or "presentation" in content_type.lower():
                    file_extension = ".pptx"
                elif "word" in content_type.lower() or "document" in content_type.lower():
                    file_extension = ".docx"
                elif "excel" in content_type.lower() or "spreadsheet" in content_type.lower():
                    file_extension = ".xlsx"
                else:
                    file_extension = ""

            storage_filename = f"{uuid.uuid4()}{file_extension}"

            # Upload to Google Cloud Storage
            try:
                # Create blob path with folder prefix
                folder_prefix = os.environ.get("GCS_FOLDER_PREFIX", "uploads")
                blob_path = f"{folder_prefix}/{storage_filename}"
                blob = self.bucket.blob(blob_path)

                # Upload file with content type
                blob.upload_from_filename(temp_file_path, content_type=content_type)

                # Generate a public URL for the file
                if os.environ.get("GCS_MAKE_PUBLIC", "").lower() == "true":
                    blob.make_public()
                    public_url = blob.public_url
                else:
                    # Generate a signed URL that expires after a period
                    expiration = int(
                        os.environ.get("GCS_URL_EXPIRATION", "86400")
                    )  # Default 24 hours
                    public_url = blob.generate_signed_url(
                        version="v4", expiration=expiration, method="GET"
                    )

                logger.info(f"File uploaded to GCS: {blob_path}")

                # Delete temp file when done
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                    temp_file_path = None

                # Store GCS path for internal reference
                bucket_name = os.environ.get("GCS_BUCKET_NAME")
                gcs_path = f"gs://{bucket_name}/{blob_path}"

                # Return file info
                file_info = {
                    "url": public_url,
                    "name": file_name,
                    "type": content_type,
                    "size": file_size,
                    "source": "url",
                    "gcs_path": gcs_path,
                }

                return True, "File processed successfully", file_info

            except Exception as gcs_error:
                logger.error(f"Failed to upload to GCS: {str(gcs_error)}")
                return False, f"Failed to store file in Cloud Storage: {str(gcs_error)}", None

        except Exception as e:
            logger.error(f"Error processing file from URL: {str(e)}")
            # Clean up any temp file
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            return False, f"Error processing file: {str(e)}", None
