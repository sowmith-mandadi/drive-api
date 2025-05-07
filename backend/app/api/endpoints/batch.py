"""
API endpoints for batch job operations.
"""
import json
import os
import urllib.request
import requests
import random
from datetime import datetime
from typing import List, Optional

import pandas as pd
from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile, status

from app.core.logging import configure_logging
from app.models.batch import BatchJob, BatchJobCreate, BatchJobError, BatchJobStatus, BatchJobUpdate
from app.models.content import Content, ContentCreate, Speaker
from app.services.batch_service import BatchService
from app.services.content_processor import ContentProcessor
from app.services.drive_downloader import DriveDownloader
from app.utils.file_utils import deduplicate_file_urls
# Using stub implementation
from app.services.task_service_stub import TaskService

# Setup logging
logger = configure_logging()

router = APIRouter(prefix="/batch", tags=["Batch Operations"])

# Service instances
batch_service = BatchService()
task_service = TaskService()
content_processor = ContentProcessor()
drive_downloader = DriveDownloader(content_processor.bucket, content_processor.firestore)


@router.get("/jobs", response_model=List[BatchJob])
async def list_batch_jobs(limit: int = 100, offset: int = 0):
    """List all batch jobs with pagination."""
    jobs = batch_service.get_all_jobs(limit=limit, offset=offset)
    return jobs


@router.get("/jobs/{job_id}", response_model=BatchJob)
async def get_batch_job(job_id: str):
    """Get a specific batch job by ID."""
    job = batch_service.get_job_by_id(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Batch job with ID {job_id} not found"
        )
    return job


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def bulk_upload_content(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: Optional[str] = Form(None),
):
    """
    Upload a batch of content items via a CSV or Excel file.

    The file should contain columns matching the content metadata fields.
    Each row will be processed asynchronously and stored in the database.
    """
    try:
        # Validate file type
        file_extension = os.path.splitext(file.filename)[1].lower() if file.filename else ""
        if file_extension not in [".csv", ".xlsx", ".xls"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a CSV or Excel file",
            )

        # Read the file contents directly
        contents = await file.read()
        
        # Read the file using pandas from memory
        try:
            if file_extension == ".csv":
                # Use StringIO to read from memory instead of creating a file
                from io import StringIO
                df = pd.read_csv(StringIO(contents.decode('utf-8')))
            else:  # Excel file
                # Use BytesIO to read from memory instead of creating a file
                from io import BytesIO
                df = pd.read_excel(BytesIO(contents))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error reading file: {str(e)}",
            )

        # Validate required columns
        required_columns = ["title", "sessionId"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {', '.join(missing_columns)}",
            )

        # Check if we have any rows
        if df.empty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File contains no data rows",
            )

        # Create a batch job
        job_data = BatchJobCreate(
            job_type="content_upload",
            total_items=len(df),
            metadata={
                "filename": file.filename,
                "total_rows": len(df),
            },
            created_by=user_id,
        )

        batch_job = batch_service.create_job(job_data)
        if not batch_job:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create batch job",
            )

        # Start processing in background
        background_tasks.add_task(
            process_batch_upload,
            batch_job.id,
            contents,
            file_extension,
        )

        return {
            "job_id": batch_job.id,
            "status": batch_job.status,
            "total_items": batch_job.total_items,
            "message": "Batch upload initiated",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch upload failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process batch upload: {str(e)}",
        )


@router.delete("/jobs/{job_id}")
async def delete_batch_job(job_id: str):
    """Delete a batch job."""
    job = batch_service.get_job_by_id(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Batch job with ID {job_id} not found"
        )

    # Only allow deletion of completed or failed jobs
    if job.status not in [
        BatchJobStatus.COMPLETED,
        BatchJobStatus.FAILED,
        BatchJobStatus.CANCELLED,
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete job with status {job.status}",
        )

    success = batch_service.delete_job(job_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete batch job",
        )

    return {"message": f"Batch job with ID {job_id} deleted"}


@router.post("/jobs/{job_id}/cancel")
async def cancel_batch_job(job_id: str):
    """Cancel a batch job."""
    job = batch_service.get_job_by_id(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Batch job with ID {job_id} not found"
        )

    # Only allow cancellation of pending or processing jobs
    if job.status not in [BatchJobStatus.PENDING, BatchJobStatus.PROCESSING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel job with status {job.status}",
        )

    # Update job status
    update_data = BatchJobUpdate(
        status=BatchJobStatus.CANCELLED,
        completed_at=datetime.now(),
    )

    updated_job = batch_service.update_job(job_id, update_data)
    if not updated_job:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel batch job",
        )

    return {"message": f"Batch job with ID {job_id} cancelled"}


async def process_batch_upload(job_id: str, contents: bytes, file_extension: str):
    """
    Process a batch upload file.

    Args:
        job_id: ID of the batch job.
        contents: File contents.
        file_extension: File extension.
    """
    try:
        # Update job status to processing
        batch_service.mark_job_processing(job_id)

        # Read the file using pandas
        try:
            if file_extension == ".csv":
                # Use StringIO to read from memory instead of creating a file
                from io import StringIO
                df = pd.read_csv(StringIO(contents.decode('utf-8')))
            else:  # Excel file
                # Use BytesIO to read from memory instead of creating a file
                from io import BytesIO
                df = pd.read_excel(BytesIO(contents))
        except Exception as e:
            logger.error(f"Failed to read file: {str(e)}")
            batch_service.mark_job_failed(job_id, f"Failed to read file: {str(e)}")
            return

        # Validate required columns
        required_columns = ["title", "sessionId"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            batch_service.mark_job_failed(
                job_id, f"Missing required columns: {', '.join(missing_columns)}"
            )
            return

        # Check if we have any rows
        if df.empty:
            batch_service.mark_job_failed(job_id, "File contains no data rows")
            return

        # Keep track of success/failure
        total_rows = len(df)
        processed_rows = 0
        successful_rows = 0
        failed_rows = 0
        
        # Keep track of large files that need background processing
        large_files_to_process = []

        # Process each row
        for index, row in df.iterrows():
            try:
                # Convert row to dict and handle NaN values
                row_dict = row.to_dict()
                row_dict = {k: (v if not pd.isna(v) else None) for k, v in row_dict.items()}

                # Parse lists and objects from strings if needed
                for key, value in row_dict.items():
                    if isinstance(value, str):
                        if value.startswith("[") and value.endswith("]"):
                            try:
                                row_dict[key] = json.loads(value)
                            except json.JSONDecodeError:
                                try:
                                    # Replace single quotes with double quotes
                                    fixed_value = value.replace("'", '"')
                                    row_dict[key] = json.loads(fixed_value)
                                except Exception:
                                    # If still fails, leave as is
                                    pass
                        elif value.startswith("{") and value.endswith("}"):
                            try:
                                row_dict[key] = json.loads(value)
                            except json.JSONDecodeError:
                                try:
                                    # Replace single quotes with double quotes
                                    fixed_value = value.replace("'", '"')
                                    row_dict[key] = json.loads(fixed_value)
                                except Exception:
                                    # If still fails, leave as is
                                    pass

                # Process job roles - convert to array if comma-separated
                job_roles = row_dict.get("jobRoles", "")
                if isinstance(job_roles, str) and "," in job_roles:
                    job_roles = [role.strip() for role in job_roles.split(",")]
                elif isinstance(job_roles, str) and job_roles:
                    job_roles = [job_roles]  # Single role as array
                else:
                    job_roles = []

                # Process areas of interest
                areas_of_interest = row_dict.get("areasOfInterest", "")
                if isinstance(areas_of_interest, str) and "," in areas_of_interest:
                    areas_of_interest = [area.strip() for area in areas_of_interest.split(",")]
                elif isinstance(areas_of_interest, str) and areas_of_interest:
                    areas_of_interest = [areas_of_interest]  # Single area as array
                else:
                    areas_of_interest = []

                # Handle tags if present
                tags = row_dict.get("tags", [])
                if isinstance(tags, str):
                    try:
                        tags = json.loads(tags)
                    except json.JSONDecodeError:
                        # Split by comma if it's a comma-separated string
                        if "," in tags:
                            tags = [tag.strip() for tag in tags.split(",")]
                        else:
                            tags = [tags]  # Treat as a single tag
                # Ensure tags is a list
                if not isinstance(tags, list):
                    tags = [str(tags)]

                # Build presenters array from individual fields
                presenters = []
                presenter_count = 6  # Maximum number of presenters we handle
                
                for i in range(1, presenter_count + 1):
                    name_key = f"presenterFullName{i}"
                    job_title_key = f"presenterJobTitle{i}"
                    company_key = f"presenterCompany{i}"
                    industry_key = f"presenterIndustry{i}"
                    
                    # Only add presenter if name exists
                    if row_dict.get(name_key):
                        presenter = {
                            "fullName": row_dict.get(name_key),
                            "jobTitle": row_dict.get(job_title_key),
                            "company": row_dict.get(company_key),
                            "industry": row_dict.get(industry_key)
                        }
                        presenters.append(presenter)

                # Initialize fileUrls array
                fileUrls = []
                
                # Add all URLs directly to fileUrls
                fileUrls = []
                
                # Handle presentation slides URL
                if row_dict.get("presentationSlidesUrl"):
                    drive_id = ""
                    if "/d/" in row_dict.get("presentationSlidesUrl", ""):
                        try:
                            drive_id = row_dict.get("presentationSlidesUrl").split("/d/")[1].split("/")[0]
                        except Exception as e:
                            logger.warning(f"Failed to extract Drive ID from presentationSlidesUrl: {e}")
                    
                    fileUrls.append({
                        "contentType": "presentation",
                        "presentation_type": "presentation_slides",
                        "name": "Presentation Slides",
                        "source": "drive",
                        "drive_url": row_dict.get("presentationSlidesUrl"),
                        "driveId": drive_id,
                        "gcs_path": None,
                        "type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        "size": 0,
                        "thumbnailLink": None,
                        "url": None
                    })
                
                # Handle recap slides URL
                if row_dict.get("recapSlidesUrl"):
                    drive_id = ""
                    if "/d/" in row_dict.get("recapSlidesUrl", ""):
                        try:
                            drive_id = row_dict.get("recapSlidesUrl").split("/d/")[1].split("/")[0]
                        except Exception as e:
                            logger.warning(f"Failed to extract Drive ID from recapSlidesUrl: {e}")
                    
                    fileUrls.append({
                        "contentType": "presentation",
                        "presentation_type": "recap_slides",
                        "name": "Recap Slides",
                        "source": "drive",
                        "drive_url": row_dict.get("recapSlidesUrl"),
                        "driveId": drive_id,
                        "gcs_path": None,
                        "type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        "size": 0,
                        "thumbnailLink": None,
                        "url": None
                    })
                
                # Handle drive link
                if row_dict.get("driveLink"):
                    drive_id = ""
                    if "/folders/" in row_dict.get("driveLink", ""):
                        try:
                            drive_id = row_dict.get("driveLink").split("/folders/")[1].split("/")[0]
                        except Exception as e:
                            logger.warning(f"Failed to extract Drive ID from driveLink: {e}")
                    elif "/d/" in row_dict.get("driveLink", ""):
                        try:
                            drive_id = row_dict.get("driveLink").split("/d/")[1].split("/")[0]
                        except Exception as e:
                            logger.warning(f"Failed to extract Drive ID from driveLink: {e}")
                            
                    fileUrls.append({
                        "contentType": "folder",
                        "presentation_type": "drive_folder",
                        "name": "Drive Folder",
                        "source": "drive",
                        "drive_url": row_dict.get("driveLink"),
                        "driveId": drive_id,
                        "gcs_path": None,
                        "url": row_dict.get("driveLink"),
                        "type": "application/vnd.google-apps.folder", 
                        "size": 0
                    })
                
                # Handle YouTube URL
                if row_dict.get("videoYoutubeUrl"):
                    # Extract YouTube ID if possible
                    youtube_id = None
                    youtube_url = row_dict.get("videoYoutubeUrl")
                    
                    if "youtube.com/watch?v=" in youtube_url:
                        try:
                            youtube_id = youtube_url.split("youtube.com/watch?v=")[1].split("&")[0]
                        except Exception:
                            pass
                    elif "youtu.be/" in youtube_url:
                        try:
                            youtube_id = youtube_url.split("youtu.be/")[1].split("?")[0]
                        except Exception:
                            pass
                    
                    fileUrls.append({
                        "contentType": "video",
                        "presentation_type": "youtube_video",
                        "name": row_dict.get("ytVideoTitle") or "YouTube Video",
                        "source": "youtube",
                        "drive_url": youtube_url,
                        "driveId": youtube_id,
                        "gcs_path": None,
                        "url": youtube_url
                    })

                # Prepare content data - maintain all fields from the original
                content_data = {
                    "title": row_dict.get("title", ""),
                    "description": row_dict.get("description", ""),
                    "abstract": row_dict.get("abstract", ""),
                    "status": row_dict.get("status", ""),
                    "track": row_dict.get("track", ""),
                    "tags": tags,
                    "sessionType": row_dict.get("sessionType", ""),
                    "demoType": row_dict.get("demoType", ""),
                    "sessionDate": row_dict.get("sessionDate"),
                    "durationMinutes": row_dict.get("durationMinutes"),
                    "learningLevel": row_dict.get("learningLevel"),
                    "industry": row_dict.get("industry"),
                    "presenters": presenters,
                    "used": False,
                    # Include the sessionId for duplicate checking
                    "sessionId": row_dict.get("sessionId"),
                    # Add source if provided, default to "upload"
                    "source": row_dict.get("source", "upload"),
                    # Job roles and areas of interest
                    "jobRoles": job_roles,
                    "areasOfInterest": areas_of_interest,
                    # Keep all original URL fields for backward compatibility
                    "presentationSlidesUrl": row_dict.get("presentationSlidesUrl"),
                    "recapSlidesUrl": row_dict.get("recapSlidesUrl"),
                    "videoRecordingStatus": row_dict.get("videoRecordingStatus"),
                    "videoYoutubeUrl": row_dict.get("videoYoutubeUrl"),
                    "ytVideoTitle": row_dict.get("ytVideoTitle"),
                    "ytDescription": row_dict.get("ytDescription"),
                    # Set fileUrls directly
                    "fileUrls": fileUrls,
                    # Include metadata
                    "metadata": {
                        "title": row_dict.get("title", ""),
                        "abstract": row_dict.get("abstract"),
                        "status": row_dict.get("status"),
                        "track": row_dict.get("track"),
                        "sessionType": row_dict.get("sessionType"),
                        "demoType": row_dict.get("demoType"),
                        "sessionDate": row_dict.get("sessionDate"),
                        "durationMinutes": row_dict.get("durationMinutes"),
                        "learningLevel": row_dict.get("learningLevel"),
                        "jobRoles": job_roles,
                        "areasOfInterest": areas_of_interest,
                        "industry": row_dict.get("industry"),
                        "presentationSlidesUrl": row_dict.get("presentationSlidesUrl"),
                        "recapSlidesUrl": row_dict.get("recapSlidesUrl"),
                        "videoRecordingStatus": row_dict.get("videoRecordingStatus"),
                        "videoYoutubeUrl": row_dict.get("videoYoutubeUrl"),
                        "ytVideoTitle": row_dict.get("ytVideoTitle"),
                        "ytDescription": row_dict.get("ytDescription")
                    }
                }

                # Process file URL if present
                file_url = row_dict.get("fileUrl")
                drive_file_id = row_dict.get("driveFileId")
                
                # Handle driveLink if it exists - store it in driveLink for compatibility
                if row_dict.get("driveLink"):
                    drive_link = row_dict.get("driveLink")
                    content_data["driveLink"] = drive_link

                # Process the content item and include file URLs
                success, message, created_content = await content_processor.process_content_item(
                    content_data, file_url, drive_file_id
                )

                # Update fileUrls with processed information
                if success and created_content and "fileUrls" in created_content:
                    # Direct mapping from processed fileUrls
                    processed_urls = {}
                    
                    # Extract the file URLs with gcs_path values
                    for item in created_content["fileUrls"]:
                        # Use presentation_type as the key for matching
                        p_type = item.get("presentation_type")
                        if p_type:
                            processed_urls[p_type] = item
                        # Also store by URL as fallback if URL exists
                        elif item.get("url"):
                            processed_urls[item.get("url")] = item
                    
                    # Get processed presentationSlidesUrl and recapSlidesUrl
                    # The logs show that these are set to the downloadable URLs
                    pres_url = created_content.get("presentationSlidesUrl")
                    recap_url = created_content.get("recapSlidesUrl")
                    
                    if pres_url:
                        logger.info(f"Using presentationSlidesUrl from processor: {pres_url}")
                    if recap_url:
                        logger.info(f"Using recapSlidesUrl from processor: {recap_url}")
                    
                    # Update our fileUrls entries
                    for entry in content_data["fileUrls"]:
                        ptype = entry.get("presentation_type")
                        
                        # First try to match by presentation_type (most reliable)
                        if ptype and ptype in processed_urls:
                            p_info = processed_urls[ptype]
                            logger.info(f"Found matching processed entry for {ptype} with gcs_path: {p_info.get('gcs_path')}")
                            # Check if we have a gcs_path - only update if available
                            if p_info.get("gcs_path"):
                                entry["gcs_path"] = p_info.get("gcs_path")
                                entry["url"] = p_info.get("url")
                                entry["thumbnailLink"] = p_info.get("thumbnailLink")
                                entry["type"] = p_info.get("type")
                                entry["size"] = p_info.get("size")
                            
                            # Handle direct export URLs for large files - always add exportUrl if available
                            if p_info.get("exportUrl"):
                                entry["exportUrl"] = p_info.get("exportUrl")
                                logger.info(f"Using direct export URL for {ptype}: {p_info.get('exportUrl')}")
                                
                                # If we don't have a URL but have exportUrl, use it
                                if not entry.get("url") or not p_info.get("gcs_path"):
                                    entry["url"] = p_info.get("exportUrl")
                                    logger.info(f"Using direct export URL for {ptype} due to file size limitations")
                            
                            # Handle tooLargeToExport flag
                            if p_info.get("tooLargeToExport") is True:
                                entry["tooLargeToExport"] = True
                                # Ensure we have a fallback URL (webViewLink)
                                if p_info.get("webViewLink"):
                                    entry["webViewLink"] = p_info.get("webViewLink")
                                    if not entry.get("url"):
                                        entry["url"] = p_info.get("webViewLink")
                                        logger.info(f"Using webViewLink for {ptype} as fallback")
                                
                                # If we have a driveId, generate a direct export URL for presentations
                                if p_info.get("driveId") and (ptype == "presentation_slides" or ptype == "recap_slides"):
                                    drive_id = p_info.get("driveId")
                                    direct_export_url = f"https://docs.google.com/presentation/d/{drive_id}/export/pptx"
                                    entry["exportUrl"] = direct_export_url
                                    entry["url"] = direct_export_url
                                    logger.info(f"Generated direct export URL for large file {ptype}: {direct_export_url}")
                            
                        # Handle presentation slides with URL fallback
                        elif ptype == "presentation_slides" and pres_url:
                            if pres_url in processed_urls:
                                p_info = processed_urls[pres_url]
                                logger.info(f"Found matching processed entry for presentation_slides with gcs_path: {p_info.get('gcs_path')}")
                                
                                # Only update these if we have a gcs_path
                                if p_info.get("gcs_path"):
                                    entry["gcs_path"] = p_info.get("gcs_path")
                                    entry["url"] = pres_url  # Use the processed URL
                                    entry["thumbnailLink"] = p_info.get("thumbnailLink")
                                    entry["type"] = p_info.get("type")
                                    entry["size"] = p_info.get("size")
                                
                                # Handle direct export URLs for large files
                                if p_info.get("exportUrl"):
                                    entry["exportUrl"] = p_info.get("exportUrl")
                                    logger.info(f"Using direct export URL for presentation_slides due to file size limitations")
                                    
                                    # If we don't have a URL but have exportUrl, use it
                                    if not entry.get("url"):
                                        entry["url"] = p_info.get("exportUrl")
                                
                                # Handle tooLargeToExport flag
                                if p_info.get("tooLargeToExport") is True:
                                    entry["tooLargeToExport"] = True
                                    # If we have a driveId, generate a direct export URL
                                    if p_info.get("driveId"):
                                        drive_id = p_info.get("driveId")
                                        direct_export_url = f"https://docs.google.com/presentation/d/{drive_id}/export/pptx"
                                        entry["exportUrl"] = direct_export_url
                                        entry["url"] = direct_export_url
                                        logger.info(f"Generated direct export URL for large presentation: {direct_export_url}")
                            else:
                                # If no match found, set the URL directly
                                logger.info(f"No matching processed entry, setting url directly: {pres_url}")
                                entry["url"] = pres_url
                        
                        # Handle recap slides with URL fallback
                        elif ptype == "recap_slides" and recap_url:
                            if recap_url in processed_urls:
                                r_info = processed_urls[recap_url]
                                logger.info(f"Found matching processed entry for recap_slides with gcs_path: {r_info.get('gcs_path')}")
                                
                                # Only update these if we have a gcs_path
                                if r_info.get("gcs_path"):
                                    entry["gcs_path"] = r_info.get("gcs_path")
                                    entry["url"] = recap_url  # Use the processed URL
                                    entry["thumbnailLink"] = r_info.get("thumbnailLink")
                                    entry["type"] = r_info.get("type")
                                    entry["size"] = r_info.get("size")
                                
                                # Handle direct export URLs for large files
                                if r_info.get("exportUrl"):
                                    entry["exportUrl"] = r_info.get("exportUrl")
                                    logger.info(f"Using direct export URL for recap_slides due to file size limitations")
                                    
                                    # If we don't have a URL but have exportUrl, use it
                                    if not entry.get("url"):
                                        entry["url"] = r_info.get("exportUrl")
                                
                                # Handle tooLargeToExport flag
                                if r_info.get("tooLargeToExport") is True:
                                    entry["tooLargeToExport"] = True
                                    # If we have a driveId, generate a direct export URL
                                    if r_info.get("driveId"):
                                        drive_id = r_info.get("driveId")
                                        direct_export_url = f"https://docs.google.com/presentation/d/{drive_id}/export/pptx"
                                        entry["exportUrl"] = direct_export_url
                                        entry["url"] = direct_export_url
                                        logger.info(f"Generated direct export URL for large recap slides: {direct_export_url}")
                            else:
                                # If no match found, set the URL directly
                                logger.info(f"No matching processed entry, setting url directly: {recap_url}")
                                entry["url"] = recap_url
                
                # Normalize fileUrls before deduplication
                for entry in content_data["fileUrls"]:
                    # Remove iconLink if it exists
                    if "iconLink" in entry:
                        del entry["iconLink"]
                    # Convert webViewLink to drive_url if it exists 
                    if "webViewLink" in entry:
                        entry["drive_url"] = entry["webViewLink"]
                        del entry["webViewLink"]
                    
                    # Ensure presentation_type is always set correctly
                    if entry.get("contentType") == "video" and not entry.get("presentation_type"):
                        entry["presentation_type"] = "youtube_video"
                    elif entry.get("contentType") == "folder" and not entry.get("presentation_type"):
                        entry["presentation_type"] = "drive_folder"
                        
                    # Normalize content types - ensure consistent casing and formatting
                    if entry.get("presentation_type") == "presentation_slides":
                        entry["presentation_type"] = "presentation_slides"
                        entry["contentType"] = "presentation"
                    elif entry.get("presentation_type") == "recap_slides":
                        entry["presentation_type"] = "recap_slides"
                        entry["contentType"] = "presentation"
                    elif entry.get("presentation_type") == "youtube_video":
                        entry["presentation_type"] = "youtube_video"
                        entry["contentType"] = "video"
                    elif entry.get("presentation_type") == "drive_folder":
                        entry["presentation_type"] = "drive_folder"
                        entry["contentType"] = "folder"
                
                # Deduplicate fileUrls using the utility function
                content_data["fileUrls"] = deduplicate_file_urls(content_data["fileUrls"])
                
                # Log all the fileUrls entries for debugging
                logger.info(f"Content item total fileUrls: {len(content_data['fileUrls'])}")
                for i, entry in enumerate(content_data["fileUrls"]):
                    logger.info(f"fileUrls[{i}] presentation_type: {entry.get('presentation_type')}, "
                              f"contentType: {entry.get('contentType')}, "
                              f"gcs_path: {entry.get('gcs_path')}, "
                              f"url: {entry.get('url')}")
                
                # Update progress
                processed_rows += 1

                if success:
                    successful_rows += 1
                    batch_service.update_job_progress(job_id, processed=1, successful=1)
                else:
                    failed_rows += 1
                    error = BatchJobError(
                        row=index,
                        message=message,
                        details=row_dict,
                    )
                    batch_service.update_job_progress(job_id, processed=1, failed=1, error=error)

                # Check for large files that need direct download
                for entry in content_data["fileUrls"]:
                    needs_background_processing = False
                    
                    # Check if this entry is marked as too large to export
                    if entry.get("tooLargeToExport") is True:
                        needs_background_processing = True
                        logger.info(f"Found file marked as too large to export: {entry.get('presentation_type')}")
                    
                    # Check if it has an exportUrl but no gcs_path
                    elif entry.get("exportUrl") and not entry.get("gcs_path"):
                        needs_background_processing = True
                        logger.info(f"Found file with exportUrl but no gcs_path: {entry.get('presentation_type')}")
                    
                    # Check if it's a presentation with a driveId but no gcs_path
                    elif entry.get("driveId") and not entry.get("gcs_path") and entry.get("presentation_type") in ["presentation_slides", "recap_slides"]:
                        needs_background_processing = True
                        logger.info(f"Found presentation with driveId but no gcs_path: {entry.get('presentation_type')}")
                    
                    if needs_background_processing and entry.get("presentation_type") in ["presentation_slides", "recap_slides"]:
                        # Log details about the file
                        logger.info(f"Found large file needing background processing: {entry.get('presentation_type')}")
                        logger.info(f"File details: driveId={entry.get('driveId')}, tooLargeToExport={entry.get('tooLargeToExport')}")
                        logger.info(f"Export URL: {entry.get('exportUrl')}")
                        
                        # Ensure we have an exportUrl for presentations
                        if not entry.get("exportUrl") and entry.get("driveId"):
                            entry["exportUrl"] = f"https://docs.google.com/presentation/d/{entry.get('driveId')}/export/pptx"
                            logger.info(f"Generated export URL for background processing: {entry['exportUrl']}")
                        
                        # Add to queue for background processing - include the content_id from the created_content
                        if created_content:
                            # Get the content ID from the created_content dictionary
                            content_id = None
                            
                            # First check if the ID is in created_content (our updated processor now adds it)
                            if created_content.get("id"):
                                content_id = created_content.get("id")
                                logger.info(f"Found content ID in returned data: {content_id}")
                            # As fallback, try to get it from logging context if possible
                            elif "_id" in created_content:
                                content_id = created_content.get("_id")
                                logger.info(f"Found content ID as '_id': {content_id}")
                            
                            if content_id:
                                large_files_to_process.append({
                                    "entry": entry,
                                    "content_id": content_id
                                })
                                logger.info(f"Queued large {entry.get('presentation_type')} for background download with content_id: {content_id}")
                            else:
                                logger.warning(f"Skipping background processing for {entry.get('presentation_type')} - missing content ID")
                        else:
                            logger.warning(f"Skipping background processing for {entry.get('presentation_type')} - missing content data")

            except Exception as e:
                # Log error
                logger.error(f"Error processing row {index}: {str(e)}")

                # Create error record
                error = BatchJobError(
                    row=index,
                    message=f"Failed to process row: {str(e)}",
                    details=row.to_dict(),
                )

                # Update progress
                processed_rows += 1
                failed_rows += 1

                # Update job progress with error
                batch_service.update_job_progress(job_id, processed=1, failed=1, error=error)

            # Progress updates every 10 rows (or configure as needed)
            if processed_rows % 10 == 0:
                logger.info(f"Processed {processed_rows}/{total_rows} rows")
        
        # Process large files in background
        if large_files_to_process:
            logger.info(f"Starting background processing of {len(large_files_to_process)} large files")
            logger.info(f"Large files details: {[f['entry'].get('presentation_type') for f in large_files_to_process]}")
            
            # Process each file
            for file_info in large_files_to_process:
                try:
                    # Make sure we have all required information
                    if not file_info.get("content_id"):
                        logger.warning(f"Missing content_id for background processing of {file_info['entry'].get('presentation_type')}")
                        continue
                        
                    logger.info(f"Processing large file in background: {file_info['entry'].get('presentation_type')} for content_id: {file_info['content_id']}")
                    logger.info(f"File driveId: {file_info['entry'].get('driveId')}")
                    logger.info(f"Using export URL: {file_info['entry'].get('exportUrl')}")
                    
                    success, updated_entry = await drive_downloader.download_and_store_presentation(
                        file_info["entry"], file_info["content_id"]
                    )
                    if success:
                        logger.info(f"Successfully processed large file for content {file_info['content_id']}")
                        logger.info(f"New gcs_path: {updated_entry.get('gcs_path')}")
                        logger.info(f"New URL: {updated_entry.get('url')}")
                    else:
                        logger.warning(f"Failed to process large file for content {file_info['content_id']}")
                        logger.warning(f"Reasons may include: download failure, permissions, or storage issues")
                except Exception as file_error:
                    logger.error(f"Error in background file processing: {str(file_error)}")
                    logger.error(f"Error details: {file_error}", exc_info=True)
        else:
            logger.info("No large files queued for background processing")

        # Mark job as completed
        batch_service.mark_job_completed(job_id)

        logger.info(f"Batch upload completed: {successful_rows} successful, {failed_rows} failed")

    except Exception as e:
        logger.error(f"Batch processing failed: {str(e)}")

        # Mark job as failed
        batch_service.mark_job_failed(job_id, str(e))


async def download_and_store_large_presentation(entry, content_id):
    """
    Download large presentation file using DriveDownloader service.
    
    Args:
        entry: File entry with direct export URL
        content_id: Content ID for the item
    
    Returns:
        Success, updated entry with GCS path
    """
    try:
        logger.info(f"Starting large file download process for content_id: {content_id}")
        
        # Use the DriveDownloader service
        success, updated_entry = await drive_downloader.download_and_store_presentation(entry, content_id)
        
        if success:
            logger.info(f"Successfully downloaded and stored file to GCS: {updated_entry.get('gcs_path')}")
        else:
            logger.warning(f"Failed to download presentation file for content {content_id}")
            
        return success, updated_entry
        
    except Exception as e:
        logger.error(f"Error downloading and storing large presentation: {str(e)}", exc_info=True)
        return False, entry
