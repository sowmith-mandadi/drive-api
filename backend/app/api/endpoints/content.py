"""
API endpoints for content management.
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Body
from fastapi.responses import JSONResponse
import json
import os
import uuid
from datetime import datetime

from app.models.content import Content, ContentCreate, ContentUpdate, ContentInDB
from app.services.content_service import ContentService
from app.services.extraction_service import ExtractionService

router = APIRouter(prefix="/content", tags=["Content"])

# Service instances
content_service = ContentService()
extraction_service = ExtractionService()

@router.get("/", response_model=List[Content])
async def list_content(limit: int = 100, offset: int = 0):
    """List all content with pagination."""
    return content_service.get_all_content(limit=limit, offset=offset)

@router.get("/{content_id}", response_model=Content)
async def get_content(content_id: str):
    """Get content by ID."""
    content = content_service.get_content_by_id(content_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Content with ID {content_id} not found"
        )
    return content

@router.post("/", response_model=Content)
async def create_content(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    content_type: str = Form(...),
    source: str = Form("upload"),
    tags: str = Form("[]"),  # JSON string of tags
    metadata: str = Form("{}"),  # JSON string of metadata
    file: Optional[UploadFile] = File(None)
):
    """Create new content with optional file upload."""
    try:
        # Parse JSON strings
        tags_list = json.loads(tags)
        metadata_dict = json.loads(metadata)
        
        # Create content data
        content_data = ContentCreate(
            title=title,
            description=description,
            content_type=content_type,
            source=source,
            tags=tags_list,
            metadata=metadata_dict
        )
        
        # Create content in database
        content = content_service.create_content(content_data)
        
        # Handle file upload if provided
        if file and source == "upload":
            # Generate file path
            file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
            file_path = os.path.join(content_service.upload_dir, f"{content.id}{file_extension}")
            
            # Save file
            with open(file_path, "wb") as f:
                contents = await file.read()
                f.write(contents)
            
            # Extract text if applicable
            extracted_text = None
            page_content = None
            
            if content_type in ["pdf", "presentation"]:
                extracted_text, page_content = extraction_service.extract_text(file_path)
            
            # Update content with file path and extracted text
            if not content_service.update_content_file(content.id, file_path, extracted_text, page_content):
                # If update fails, still return the content but log the error
                # The file was saved, but the metadata update failed
                content.file_path = file_path  # Update the response object
                if extracted_text:
                    content.extracted_text = extracted_text
                if page_content:
                    content.page_content = page_content
        
        return content
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create content: {str(e)}"
        )

@router.put("/{content_id}", response_model=Content)
async def update_content(content_id: str, update_data: ContentUpdate):
    """Update existing content."""
    updated_content = content_service.update_content(content_id, update_data)
    if not updated_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Content with ID {content_id} not found"
        )
    return updated_content

@router.delete("/{content_id}")
async def delete_content(content_id: str):
    """Delete content."""
    success = content_service.delete_content(content_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Content with ID {content_id} not found"
        )
    return {"message": f"Content with ID {content_id} deleted"}

@router.post("/search", response_model=List[Content])
async def search_content(
    query: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = Body({})
):
    """Search for content with optional filters."""
    # Convert None to empty string for the service layer
    results = content_service.search_content(query or "", filters)
    return results

@router.post("/content-by-ids", response_model=List[Content])
async def get_content_by_ids(
    content_ids: List[str] = Body(..., embed=True)
):
    """Get multiple content items by their IDs."""
    try:
        if not content_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No content IDs provided"
            )
            
        contents = []
        for content_id in content_ids:
            content = content_service.get_content_by_id(content_id)
            if content:
                contents.append(content)
                
        return contents
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch content by IDs: {str(e)}"
        )

@router.get("/popular-tags", response_model=List[Dict[str, Any]])
async def get_popular_tags(limit: int = 20):
    """Get most popular tags."""
    try:
        # This would typically be implemented in the content_service
        # For now, we'll return a basic implementation
        tag_counts = content_service.get_popular_tags(limit)
        return tag_counts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch popular tags: {str(e)}"
        )

@router.get("/recent-content", response_model=Dict[str, Any])
async def get_recent_content(page: int = 1, page_size: int = 10):
    """Get recent content with pagination."""
    try:
        result = content_service.get_recent_content(page, page_size)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch recent content: {str(e)}"
        ) 