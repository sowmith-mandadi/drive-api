"""
API endpoints for Google Drive integration.
"""
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core.auth import GOOGLE_AUTH_DISABLED, get_current_user_credentials
from app.models.content import DriveFile, DriveImportRequest
from app.schemas.drive import DriveFolder
from app.services.drive_service import DriveService

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/drive", tags=["Drive"])


class DriveFileList(BaseModel):
    """Model for a list of Google Drive files."""

    files: List[DriveFile]
    next_page_token: Optional[str] = None


class GoogleAuthResponse(BaseModel):
    """Model for Google auth response."""

    auth_url: str


class GoogleCallbackResponse(BaseModel):
    """Model for Google callback response."""

    success: bool
    message: str


@router.get(
    "/drive/files",
    response_model=DriveFileList,
    summary="List Google Drive files",
    description="Returns a list of files from Google Drive",
)
async def list_drive_files(
    request: Request,
    page_size: int = Query(10, gt=0, le=100, description="Number of files to return"),
    page_token: Optional[str] = Query(None, description="Token for pagination"),
    credentials: Dict[str, Any] = Depends(get_current_user_credentials),
) -> Dict[str, Any]:
    """
    List files from Google Drive.

    Args:
        request (Request): FastAPI request object
        page_size (int): Number of files to return
        page_token (Optional[str]): Token for pagination
        credentials (Dict[str, Any]): User's Google credentials

    Returns:
        Dict[str, Any]: List of files from Google Drive

    Raises:
        HTTPException: If there is an error listing files
    """
    try:
        # Check if OAuth is disabled
        if GOOGLE_AUTH_DISABLED:
            logger.info("Drive API is disabled, returning mock data")
            return {
                "files": [
                    {
                        "id": "mock_file_1",
                        "name": "Sample Document.docx",
                        "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        "web_view_link": "https://example.com/sample",
                        "thumbnail_link": None,
                        "modified_time": "2025-05-01T10:00:00Z",
                        "size": 12345,
                    },
                    {
                        "id": "mock_file_2",
                        "name": "Example Presentation.pptx",
                        "mime_type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        "web_view_link": "https://example.com/example",
                        "thumbnail_link": None,
                        "modified_time": "2025-05-01T11:00:00Z",
                        "size": 54321,
                    },
                ],
                "next_page_token": None,
            }

        # Check if using mock credentials (OAuth not fully configured)
        if credentials.get("mock"):
            logger.info("Using mock credentials, returning sample data")
            return {
                "files": [
                    {
                        "id": "sample_file_1",
                        "name": "Example Document.docx",
                        "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        "web_view_link": "https://example.com/doc",
                        "thumbnail_link": None,
                        "modified_time": "2025-05-01T09:00:00Z",
                        "size": 23456,
                    }
                ],
                "next_page_token": None,
            }

        # Import Google API client
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        # Build credential object
        creds = Credentials(
            token=credentials.get("token"),
            refresh_token=credentials.get("refresh_token"),
            token_uri=credentials.get("token_uri", "https://oauth2.googleapis.com/token"),
            client_id=credentials.get("client_id"),
            client_secret=credentials.get("client_secret"),
            scopes=credentials.get("scopes"),
        )

        # Build Google Drive service
        service = build("drive", "v3", credentials=creds)

        # List files
        fields = "files(id,name,mimeType,webViewLink,thumbnailLink,modifiedTime,size),nextPageToken"
        results = (
            service.files()
            .list(
                pageSize=page_size,
                pageToken=page_token,
                fields=fields,
                orderBy="modifiedTime desc",
            )
            .execute()
        )

        # Process results
        files = results.get("files", [])
        next_page_token = results.get("nextPageToken")

        # Convert to API response format
        file_list = []
        for file in files:
            file_list.append(
                {
                    "id": file.get("id", ""),
                    "name": file.get("name", ""),
                    "mime_type": file.get("mimeType", ""),
                    "web_view_link": file.get("webViewLink"),
                    "thumbnail_link": file.get("thumbnailLink"),
                    "modified_time": file.get("modifiedTime"),
                    "size": file.get("size"),
                }
            )

        return {"files": file_list, "next_page_token": next_page_token}
    except Exception as e:
        logger.error(f"Failed to list Drive files: {str(e)}")
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

        # Check if OAuth is disabled
        if GOOGLE_AUTH_DISABLED:
            logger.warning("Drive auth is disabled, returning mock URL")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"auth_url": "https://example.com/oauth-disabled", "oauth_disabled": True},
            )

        # Use OAuth utilities directly since we don't have credentials yet
        from app.core.auth import google_oauth

        # This will throw an appropriate HTTP exception if OAuth is misconfigured
        auth_url = google_oauth.get_authorization_url()
        return {"auth_url": auth_url}
    except HTTPException:
        # Pass through specific HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Failed to generate auth URL: {str(e)}")
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

        # Check if OAuth is disabled
        if GOOGLE_AUTH_DISABLED:
            logger.warning("OAuth callback received while OAuth is disabled")
            return {
                "success": True,
                "message": "OAuth is disabled, but the callback was received",
                "oauth_disabled": True,
            }

        # Use OAuth utilities directly
        from app.core.auth import google_oauth

        # This will throw an appropriate HTTP exception if OAuth is misconfigured
        credentials = google_oauth.exchange_code(code)

        # Store credentials in session
        request.session["credentials"] = credentials

        return {
            "success": True,
            "message": "Authentication successful",
        }
    except HTTPException:
        # Pass through specific HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"OAuth callback processing failed: {str(e)}")
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
        logger.error(f"Failed to list folders: {str(e)}")
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
        logger.info(f"Listing files in folder {folder_id}")
        drive_service = DriveService(credentials)

        # In a real implementation, we would use a proper folder query
        # This is a simplified version
        all_files = drive_service.list_files()
        folder_files = [file for file in all_files if folder_id in file.get("parents", [])]
        return folder_files
    except Exception as e:
        logger.error(f"Failed to list files in folder {folder_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list files in folder: {str(e)}",
        )
