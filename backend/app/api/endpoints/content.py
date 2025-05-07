"""
API endpoints for content management.
"""
import json
import os
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, File, Form, HTTPException, UploadFile, status

from app.models.content import Content, ContentCreate, ContentUpdate
from app.services.content_service import ContentService
from app.services.extraction_service import ExtractionService

router = APIRouter(prefix="/content", tags=["Content"])

# Service instances
content_service = ContentService()
extraction_service = ExtractionService()


@router.get("/", response_model=List[Content])
async def list_content(limit: int = 100, offset: int = 0) -> List[Content]:
    """List all content with pagination."""
    content_items = content_service.get_all_content(limit=limit, offset=offset)
    # Convert ContentInDB to Content
    return [Content.model_validate(item.model_dump()) for item in content_items]


@router.get("/{content_id}", response_model=Content)
async def get_content(content_id: str) -> Content:
    """Get content by ID."""
    content = content_service.get_content_by_id(content_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Content with ID {content_id} not found"
        )
    # Convert ContentInDB to Content
    return Content.model_validate(content.model_dump())


@router.post("/", response_model=Content)
async def create_content(
    # Basic content info
    title: str = Form(...),
    description: Optional[str] = Form(None),
    content_type: str = Form(...),
    source: str = Form("upload"),
    abstract: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
    demo_type: Optional[str] = Form(None),
    # Categorization
    tags: str = Form("[]"),  # JSON string of tags
    track: Optional[str] = Form(None),
    learning_level: Optional[str] = Form(None),
    topics: Optional[str] = Form("[]"),  # JSON string
    target_job_roles: Optional[str] = Form("[]"),  # JSON string
    area_of_interest: Optional[str] = Form("[]"),  # JSON string
    # Metadata
    metadata: str = Form("{}"),  # JSON string of metadata
    duration_minutes: Optional[str] = Form(None),
    # Speakers
    speakers: Optional[str] = Form("[]"),  # JSON string of speakers
    # Files
    file: Optional[UploadFile] = File(None),
    # Assets
    presentation_slides_url: Optional[str] = Form(None),
    recap_slides_url: Optional[str] = Form(None),
    video_recording_status: Optional[str] = Form(None),
) -> Content:
    """Create new content with optional file upload."""
    try:
        # Parse JSON strings
        tags_list = json.loads(tags)
        metadata_dict = json.loads(metadata)
        speakers_list = json.loads(speakers) if speakers else []
        topics_list = json.loads(topics) if topics else []
        target_job_roles_list = json.loads(target_job_roles) if target_job_roles else []
        area_of_interest_list = json.loads(area_of_interest) if area_of_interest else []

        # Create content data with camelCase field names
        content_data = ContentCreate(
            title=title,
            description=description,
            contentType=content_type,  # Use camelCase for model
            source=source,
            tags=tags_list,
            metadata=metadata_dict,
            fileId=None,  # Set explicitly
        )

        # Create content in database
        content = content_service.create_content(content_data)

        # Update with additional fields that are not part of ContentCreate
        # Using snake_case for Firestore fields
        additional_data = {
            "abstract": abstract,
            "session_id": session_id,
            "status": status,
            "demo_type": demo_type,
            "track": track,
            "learning_level": learning_level,
            "topics": topics_list,
            "target_job_roles": target_job_roles_list,
            "area_of_interest": area_of_interest_list,
            "speakers": speakers_list,
            "duration_minutes": duration_minutes,
            "presentation_slides_url": presentation_slides_url,
            "recap_slides_url": recap_slides_url,
            "video_recording_status": video_recording_status,
        }

        # Remove None values
        additional_data = {k: v for k, v in additional_data.items() if v is not None}

        # Update content with additional fields
        if additional_data:
            content_service.update_content_fields(content.id, additional_data)
            # Refresh content with updated fields
            content = content_service.get_content_by_id(content.id)

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
            if not content_service.update_content_file(
                content.id, file_path, extracted_text, page_content
            ):
                # If update fails, still return the content but log the error
                # The file was saved, but the metadata update failed
                content.filePath = file_path  # Update using camelCase
                if extracted_text:
                    content.extractedText = extracted_text  # Use camelCase
                if page_content:
                    content.pageContent = page_content  # Use camelCase

        # Convert ContentInDB to Content
        return Content.model_validate(content.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create content: {str(e)}",
        )


@router.put("/{content_id}", response_model=Content)
async def update_content(content_id: str, update_data: ContentUpdate) -> Content:
    """Update existing content."""
    updated_content = content_service.update_content(content_id, update_data)
    if not updated_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Content with ID {content_id} not found"
        )
    # Convert ContentInDB to Content
    return Content.model_validate(updated_content.model_dump())


@router.put("/{content_id}/fields", response_model=Content)
async def update_content_fields(content_id: str, fields: Dict[str, Any] = Body(...)) -> Content:
    """Update specific fields of existing content."""
    updated_content = content_service.update_content_fields(content_id, fields)
    if not updated_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Content with ID {content_id} not found"
        )
    # Convert ContentInDB to Content
    return Content.model_validate(updated_content.model_dump())


@router.delete("/{content_id}")
async def delete_content(content_id: str) -> Dict[str, str]:
    """Delete content."""
    success = content_service.delete_content(content_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Content with ID {content_id} not found"
        )
    return {"message": f"Content with ID {content_id} deleted"}


@router.post("/search", response_model=List[Content])
async def search_content(
    query: Optional[str] = None, filters: Optional[Dict[str, Any]] = Body({})
) -> List[Content]:
    """Search for content with optional filters."""
    # Convert None to empty string for the service layer
    results = content_service.search_content(query or "", filters)
    # Convert ContentInDB to Content
    return [Content.model_validate(item.model_dump()) for item in results]


@router.post("/content-by-ids", response_model=List[Content])
async def get_content_by_ids(content_ids: List[str] = Body(..., embed=True)) -> List[Content]:
    """Get multiple content items by their IDs."""
    try:
        if not content_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="No content IDs provided"
            )

        contents = []
        for content_id in content_ids:
            content = content_service.get_content_by_id(content_id)
            if content:
                # Convert ContentInDB to Content
                contents.append(Content.model_validate(content.model_dump()))

        return contents
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch content by IDs: {str(e)}",
        )


@router.get("/popular-tags", response_model=List[Dict[str, Any]])
async def get_popular_tags(limit: int = 20) -> List[Dict[str, Any]]:
    """Get most popular tags."""
    try:
        # This would typically be implemented in the content_service
        # For now, we'll return a basic implementation
        tag_counts = content_service.get_popular_tags(limit)
        return tag_counts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch popular tags: {str(e)}",
        )


@router.get("/recent-content", response_model=Dict[str, Any])
async def get_recent_content(page: int = 1, page_size: int = 10) -> Dict[str, Any]:
    """Get recent content with pagination."""
    try:
        result = content_service.get_recent_content(page, page_size)
        # Convert items from ContentInDB to Content
        if "items" in result:
            result["items"] = [
                Content.model_validate(item.model_dump()) for item in result["items"]
            ]
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch recent content: {str(e)}",
        )
@router.get("/", response_model=List[Content])
async def list_content(limit: int = 100, offset: int = 0) -> List[Content]:
    """List all content with pagination."""
    print("\n\nDEBUG: API list_content called with limit:", limit, "offset:", offset)
    content_items = content_service.get_all_content(limit=limit, offset=offset)
    print(f"DEBUG: API received {len(content_items)} items from service")
    
    # Debug the model validation
    result = []
    for item in content_items:
        try:
            validated = Content.model_validate(item.model_dump())
            result.append(validated)
            print(f"DEBUG: Successfully validated content item {item.id} -> {validated.id}")
        except Exception as e:
            print(f"DEBUG: Error validating content item: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print(f"DEBUG: API returning {len(result)} validated items")
    return result

@router.get("/test-firestore", response_model=Dict[str, Any])
async def test_firestore():
    """Test Firestore connection and collection access."""
    from app.db.firestore_client import FirestoreClient
    from app.core.config import settings
    import datetime
    import uuid
    import traceback
    
    result = {
        "success": False,
        "collections": [],
        "test_write": False,
        "errors": []
    }
    
    try:
        # Initialize client
        firestore = FirestoreClient()
        result["client_initialized"] = True
        
        # Get settings
        result["project_id"] = settings.FIRESTORE_PROJECT_ID
        result["collection"] = settings.FIRESTORE_COLLECTION_CONTENT
        
        # List collections
        collections = firestore.db.collections()
        for col in collections:
            result["collections"].append(col.id)
            
        # Try to read from content collection 
        collection = settings.FIRESTORE_COLLECTION_CONTENT
        docs = list(firestore.db.collection(collection).limit(5).stream())
        result["documents_found"] = len(docs)
        
        # If no documents, try to create a test one
        if len(docs) == 0:
            # Try a different capitalization
            alt_collection = "Content" if collection == "content" else "content"
            alt_docs = list(firestore.db.collection(alt_collection).limit(5).stream())
            result["alt_documents_found"] = len(alt_docs)
            result["alt_collection"] = alt_collection
            
            # Create a test document
            test_id = f"test-{uuid.uuid4()}"
            test_data = {
                "title": "Test Document",
                "description": "Created for testing Firestore access",
                "content_type": "test",
                "created_at": datetime.datetime.now().isoformat(),
                "updated_at": datetime.datetime.now().isoformat()
            }
            
            # Try to write to both collections
            try:
                firestore.db.collection(collection).document(test_id).set(test_data)
                result["test_write"] = True
                result["test_write_collection"] = collection
                result["test_document_id"] = test_id
            except Exception as write_err:
                result["errors"].append(f"Write error: {str(write_err)}")
                # Try alternate collection
                try:
                    firestore.db.collection(alt_collection).document(test_id).set(test_data)
                    result["test_write"] = True
                    result["test_write_collection"] = alt_collection
                    result["test_document_id"] = test_id
                except Exception as alt_write_err:
                    result["errors"].append(f"Alt write error: {str(alt_write_err)}")
        
        result["success"] = True
    except Exception as e:
        result["errors"].append(f"Error: {str(e)}")
        result["traceback"] = traceback.format_exc()
        
    return result

@router.get("/test-firestore", response_model=Dict[str, Any])
async def test_firestore():
    """Test Firestore connection and collection access."""
    from app.db.firestore_client import FirestoreClient
    from app.core.config import settings
    import datetime
    import uuid
    import traceback
    
    result = {
        "success": False,
        "collections": [],
        "test_write": False,
        "errors": []
    }
    
    try:
        # Initialize client
        firestore = FirestoreClient()
        result["client_initialized"] = True
        
        # Get settings
        result["project_id"] = settings.FIRESTORE_PROJECT_ID
        result["collection"] = settings.FIRESTORE_COLLECTION_CONTENT
        
        # List collections
        collections = firestore.db.collections()
        for col in collections:
            result["collections"].append(col.id)
            
        # Try to read from content collection 
        collection = settings.FIRESTORE_COLLECTION_CONTENT
        docs = list(firestore.db.collection(collection).limit(5).stream())
        result["documents_found"] = len(docs)
        
        # If no documents, try to create a test one
        if len(docs) == 0:
            # Try a different capitalization
            alt_collection = "Content" if collection == "content" else "content"
            alt_docs = list(firestore.db.collection(alt_collection).limit(5).stream())
            result["alt_documents_found"] = len(alt_docs)
            result["alt_collection"] = alt_collection
            
            # Create a test document
            test_id = f"test-{uuid.uuid4()}"
            test_data = {
                "title": "Test Document",
                "description": "Created for testing Firestore access",
                "content_type": "test",
                "created_at": datetime.datetime.now().isoformat(),
                "updated_at": datetime.datetime.now().isoformat()
            }
            
            # Try to write to both collections
            try:
                firestore.db.collection(collection).document(test_id).set(test_data)
                result["test_write"] = True
                result["test_write_collection"] = collection
                result["test_document_id"] = test_id
            except Exception as write_err:
                result["errors"].append(f"Write error: {str(write_err)}")
                # Try alternate collection
                try:
                    firestore.db.collection(alt_collection).document(test_id).set(test_data)
                    result["test_write"] = True
                    result["test_write_collection"] = alt_collection
                    result["test_document_id"] = test_id
                except Exception as alt_write_err:
                    result["errors"].append(f"Alt write error: {str(alt_write_err)}")
        
        result["success"] = True
    except Exception as e:
        result["errors"].append(f"Error: {str(e)}")
        result["traceback"] = traceback.format_exc()
        
    return result
