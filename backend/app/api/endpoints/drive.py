"""
API endpoints for Google Drive integration.
"""
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel

from app.core.auth import get_current_user_credentials
from app.core.logging import configure_logging
from app.models.content import DriveFile, DriveImportRequest
from app.schemas.drive import DriveFolder
from app.services.drive_service import DriveService

# Set up logger
logger = configure_logging()

router = APIRouter(prefix="/drive", tags=["Drive"])


class GoogleAuthResponse(BaseModel):
    """Response model for Google authentication."""

    auth_url: str


class GoogleCallbackResponse(BaseModel):
    """Response model for Google authentication callback."""

    success: bool
    message: str


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
            detail=f"Failed to list Drive files: {str(e)}",
        )


@router.get("/files/{file_id}", response_model=DriveFile)
async def get_drive_file(
    file_id: str, credentials: Dict[str, Any] = Depends(get_current_user_credentials)
):
    """Get metadata for a specific Drive file."""
    try:
        drive_service = DriveService(credentials)
        file = drive_service.get_file_metadata(file_id)
        return file
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Drive file metadata: {str(e)}",
        )


@router.post("/import", response_model=Dict[str, Any])
async def import_drive_files(
    import_request: DriveImportRequest,
    credentials: Dict[str, Any] = Depends(get_current_user_credentials),
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
            "metadata": import_request.metadata,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to import Drive files: {str(e)}",
        )


@router.get(
    "/drive/auth",
    response_model=GoogleAuthResponse,
    summary="Get Google Drive authorization URL",
    description="Generates a URL for Google Drive authorization",
)
async def get_auth_url() -> Dict[str, str]:
    """
    Get the Google Drive authentication URL.

    Returns:
        Dict[str, str]: A dictionary containing the authentication URL

    Raises:
        HTTPException: If there is an error generating the authentication URL
    """
    try:
        logger.info("Generating Google Drive auth URL")
        # Use OAuth utilities directly since we don't have credentials yet
        from app.core.auth import google_oauth

        auth_url = google_oauth.get_authorization_url()
        return {"auth_url": auth_url}
    except Exception as e:
        logger.error("Failed to generate auth URL", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate auth URL: {str(e)}",
        )


@router.get(
    "/auth/callback",
    response_model=GoogleCallbackResponse,
    summary="Handle Google OAuth callback",
    description="Processes the callback from Google OAuth flow",
)
async def auth_callback(
    request: Request, code: str = Query(..., description="Authorization code from Google")
) -> Dict[str, Any]:
    """
    Handle the Google authentication callback.

    Args:
        code (str): The authorization code from Google OAuth

    Returns:
        Dict[str, Any]: Success status and message

    Raises:
        HTTPException: If there is an error during the authentication process
    """
    try:
        logger.info("Processing OAuth callback")
        # Use OAuth utilities directly
        from app.core.auth import google_oauth

        credentials = google_oauth.exchange_code(code)

        # Store credentials in session
        request.session["credentials"] = credentials

        return {
            "success": True,
            "message": "Authentication successful",
        }
    except Exception as e:
        logger.error("OAuth callback processing failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}",
        )


@router.get(
    "/drive/folders",
    response_model=List[DriveFolder],
    summary="List Google Drive folders",
    description="Returns a list of folders from Google Drive",
)
async def list_folders(
    credentials: Dict[str, Any] = Depends(get_current_user_credentials)
) -> List[Dict[str, Any]]:
    """
    List all folders in Google Drive.

    Returns:
        List[Dict[str, Any]]: A list of folder objects with id and name

    Raises:
        HTTPException: If there is an error accessing Google Drive or if not authenticated
    """
    try:
        logger.info("Listing Google Drive folders")
        drive_service = DriveService(credentials)

        # Filter folders from list_files results
        all_files = drive_service.list_files()
        folders = [
            file
            for file in all_files
            if file.get("mimeType") == "application/vnd.google-apps.folder"
        ]
        return folders
    except Exception as e:
        logger.error("Failed to list folders", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list folders: {str(e)}",
        )


@router.get(
    "/drive/folders/{folder_id}/files",
    response_model=List[DriveFile],
    summary="List files in a Drive folder",
    description="Returns a list of files in the specified Google Drive folder",
)
async def list_files_in_folder(
    folder_id: str, credentials: Dict[str, Any] = Depends(get_current_user_credentials)
) -> List[Dict[str, Any]]:
    """
    List all files in a specific Google Drive folder.

    Args:
        folder_id (str): The ID of the Google Drive folder

    Returns:
        List[Dict[str, Any]]: A list of file objects with metadata

    Raises:
        HTTPException: If there is an error accessing Google Drive, folder not found,
                      or if not authenticated
    """
    try:
        logger.info("Listing files in folder", folder_id=folder_id)
        drive_service = DriveService(credentials)

        # In a real implementation, we would use a proper folder query
        # This is a simplified version
        all_files = drive_service.list_files()
        folder_files = [file for file in all_files if folder_id in file.get("parents", [])]
        return folder_files
    except Exception as e:
        logger.error("Failed to list files in folder", folder_id=folder_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list files in folder: {str(e)}",
        )
