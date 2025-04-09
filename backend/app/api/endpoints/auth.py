"""
API endpoints for authentication.
"""
import json
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse

from app.core.auth import google_oauth
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/login")
async def login(request: Request):
    """Initiate Google OAuth login flow."""
    try:
        # Generate authorization URL
        authorization_url = google_oauth.get_authorization_url()

        # Redirect to Google's authorization page
        return RedirectResponse(authorization_url)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate login: {str(e)}",
        )


@router.get("/callback")
async def callback(request: Request, code: str, state: Optional[str] = None):
    """Handle callback from Google OAuth."""
    try:
        # Exchange code for credentials
        credentials = google_oauth.exchange_code(code)

        # Store credentials in session
        # In a real implementation, this would use a secure session store
        # or generate a JWT token
        request.session["credentials"] = json.dumps(credentials)

        # Redirect to frontend application
        frontend_url = settings.FRONTEND_URL or "/"
        return RedirectResponse(frontend_url)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete authentication: {str(e)}",
        )


@router.get("/logout")
async def logout(request: Request, response: Response):
    """Log out the current user."""
    # Clear session
    request.session.clear()

    # Clear cookies
    response.delete_cookie("session")

    return {"message": "Logged out successfully"}


@router.get("/status")
async def auth_status(request: Request):
    """Check authentication status."""
    credentials_str = request.session.get("credentials")
    if credentials_str:
        # Return authenticated status (don't return the actual credentials)
        return {"authenticated": True}
    else:
        return {"authenticated": False}
