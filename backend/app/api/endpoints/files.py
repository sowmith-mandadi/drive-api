"""
API endpoints for serving files.
"""
import mimetypes
import os

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse

from app.core.logging import configure_logging

# Setup logging
logger = configure_logging()

# Initialize mimetypes
mimetypes.init()

router = APIRouter(prefix="/files", tags=["Files"])


@router.get("/{file_name}")
async def get_file(file_name: str):
    """
    Serve a file from the bucket directory.

    Args:
        file_name: Name of the file to serve.

    Returns:
        FileResponse: The requested file.
    """
    # Security check - ensure file_name doesn't contain path traversal
    if ".." in file_name or "/" in file_name or "\\" in file_name:
        logger.warning(f"Security check failed for file name: {file_name}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file name",
        )

    # Construct the file path using environment variable instead of hardcoded path
    # Default to /tmp/bucket for App Engine compatibility
    bucket_dir = os.environ.get("UPLOAD_BUCKET_DIR", "/tmp/bucket")
    file_path = os.path.join(bucket_dir, file_name)

    # Check if file exists
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        logger.warning(f"File not found: {file_path}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    # Determine content type based on file extension
    content_type = None
    file_extension = os.path.splitext(file_name)[1].lower()

    if file_extension:
        content_type = mimetypes.types_map.get(file_extension)

    # If content type couldn't be determined, let FastAPI guess it
    logger.info(f"Serving file: {file_path} ({content_type or 'auto-detected content type'})")

    # Set proper headers for download if needed
    filename = os.path.basename(file_path)
    headers = {"Content-Disposition": f"inline; filename={filename}"}

    return FileResponse(
        path=file_path,
        media_type=content_type,
        headers=headers,
    )
