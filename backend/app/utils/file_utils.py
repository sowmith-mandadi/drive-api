"""
Utility functions for file handling and processing.
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def deduplicate_file_urls(file_urls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deduplicate file URLs to ensure only one entry per presentation_type.
    Prioritizes entries with gcs_path values.
    
    Args:
        file_urls: List of file URL entries
        
    Returns:
        Deduplicated list with at most one entry per presentation_type
    """
    # Dictionary to track unique presentation_types
    unique_entries = {}
    
    # First pass - collect all entries by presentation_type
    for entry in file_urls:
        ptype = entry.get("presentation_type")
        if not ptype:
            continue
            
        # If this type doesn't exist yet, add it
        if ptype not in unique_entries:
            unique_entries[ptype] = entry
        else:
            # If there's an existing entry, use entry selection logic
            existing_entry = unique_entries[ptype]
            
            # Selection priority:
            # 1. Entries with gcs_path
            # 2. Entries with exportUrl
            # 3. Entries with url
            
            if entry.get("gcs_path") and not existing_entry.get("gcs_path"):
                unique_entries[ptype] = entry
            elif (entry.get("gcs_path") and existing_entry.get("gcs_path")) or \
                 (not entry.get("gcs_path") and not existing_entry.get("gcs_path")):
                # If both have gcs_path or neither has gcs_path
                if entry.get("exportUrl") and not existing_entry.get("exportUrl"):
                    unique_entries[ptype] = entry
                elif entry.get("url") and not existing_entry.get("url"):
                    unique_entries[ptype] = entry
    
    # Build final list of only the unique entries with required fields
    result = []
    for ptype in ["presentation_slides", "recap_slides", "drive_folder", "youtube_video"]:
        if ptype in unique_entries:
            entry = unique_entries[ptype]
            clean_entry = {
                "presentation_type": ptype,
                "driveId": entry.get("driveId", ""),
                "gcs_path": entry.get("gcs_path"),  
                "url": entry.get("url"),
                "source": entry.get("source", ""),
                "thumbnailLink": entry.get("thumbnailLink"),
                "size": entry.get("size", 0),
            }
            
            # Set content type based on presentation_type
            if ptype in ["presentation_slides", "recap_slides"]:
                clean_entry["contentType"] = "presentation"
                clean_entry["type"] = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            elif ptype == "drive_folder":
                clean_entry["contentType"] = "folder"
                clean_entry["type"] = "application/vnd.google-apps.folder"
            elif ptype == "youtube_video":
                clean_entry["contentType"] = "video"
                clean_entry["type"] = "video/youtube"
            
            # Set standard name values
            if ptype == "presentation_slides":
                clean_entry["name"] = entry.get("name", "Presentation Slides")
            elif ptype == "recap_slides":
                clean_entry["name"] = entry.get("name", "Recap Slides")
            elif ptype == "drive_folder":
                clean_entry["name"] = entry.get("name", "Drive Folder")
            elif ptype == "youtube_video":
                clean_entry["name"] = entry.get("name", "YouTube Video")
            
            # Set source if not already set
            if not clean_entry["source"]:
                if ptype in ["presentation_slides", "recap_slides", "drive_folder"]:
                    clean_entry["source"] = "drive"
                elif ptype == "youtube_video":
                    clean_entry["source"] = "youtube"
            
            # Include drive_url as a reference to the original URL
            if entry.get("drive_url"):
                clean_entry["drive_url"] = entry["drive_url"]
            
            # Preserve exportUrl for large files if available
            if entry.get("exportUrl"):
                clean_entry["exportUrl"] = entry["exportUrl"]
                
            # Use exportUrl as url if url is missing but exportUrl exists
            if not clean_entry["url"] and entry.get("exportUrl"):
                clean_entry["url"] = entry["exportUrl"]
                
            # Handle webViewLink if available
            if entry.get("webViewLink"):
                clean_entry["webViewLink"] = entry["webViewLink"]
                
            # Keep track of large files with tooLargeToExport flag
            if entry.get("tooLargeToExport") is True:
                clean_entry["tooLargeToExport"] = True
                
            # Handle very large files - generate direct export URL if we have a driveId
            if ((not clean_entry["url"] or entry.get("tooLargeToExport") is True) and 
                clean_entry["driveId"] and 
                (ptype == "presentation_slides" or ptype == "recap_slides")):
                # Create a direct export URL
                drive_id = clean_entry["driveId"]
                direct_export_url = f"https://docs.google.com/presentation/d/{drive_id}/export/pptx"
                clean_entry["url"] = direct_export_url
                clean_entry["exportUrl"] = direct_export_url
                
            # Add the clean entry to the result list
            result.append(clean_entry)
    
    return result 