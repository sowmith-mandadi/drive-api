"""
API endpoints for Google Drive integration.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse

from app.models.content import DriveFile, DriveImportRequest
from app.services.drive_service import DriveService
from app.core.auth import get_current_user_credentials

router = APIRouter(prefix="/drive", tags=["Drive"])

@router.get("/files", response_model=List[DriveFile])
async def list_drive_files(credentials: Dict[str, Any] = Depends(get_current_user_credentials)):
    """List files from Google Drive."""
    try:
        drive_service = DriveService(credentials)
        files = drive_service.list_files()
        return files
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list Drive files: {str(e)}"
        )

@router.get("/files/{file_id}", response_model=DriveFile)
async def get_drive_file(
    file_id: str, 
    credentials: Dict[str, Any] = Depends(get_current_user_credentials)
):
    """Get metadata for a specific Drive file."""
    try:
        drive_service = DriveService(credentials)
        file = drive_service.get_file_metadata(file_id)
        return file
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Drive file metadata: {str(e)}"
        )

@router.post("/import", response_model=Dict[str, Any])
async def import_drive_files(
    import_request: DriveImportRequest,
    credentials: Dict[str, Any] = Depends(get_current_user_credentials)
):
    """Import files from Google Drive."""
    try:
        drive_service = DriveService(credentials)
        files = drive_service.get_files_metadata(import_request.fileIds)
        
        # In a real implementation, we would process these files further,
        # downloading them, extracting text, etc.
        
        return {
            "success": True,
            "processed": len(files),
            "files": files,
            "metadata": import_request.metadata
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to import Drive files: {str(e)}"
        ) 