"""
API endpoints for authentication.
"""
import json
import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse

from app.core.auth import GOOGLE_AUTH_DISABLED, google_oauth
from app.core.config import settings

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/login")
async def login(request: Request):
    """Initiate Google OAuth login flow."""
    try:
        # Check if OAuth is disabled
        if GOOGLE_AUTH_DISABLED:
            logger.warning("Login attempted while OAuth is disabled")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": "OAuth authentication is disabled", "oauth_disabled": True},
            )

        # Generate authorization URL
        authorization_url = google_oauth.get_authorization_url()

        # Redirect to Google's authorization page
        return RedirectResponse(authorization_url)
    except HTTPException:
        # Pass through HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Failed to initiate login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate login: {str(e)}",
        )


@router.get("/callback")
async def callback(request: Request, code: str, state: Optional[str] = None):
    """Handle callback from Google OAuth."""
    try:
        # Check if OAuth is disabled
        if GOOGLE_AUTH_DISABLED:
            logger.warning("OAuth callback received while OAuth is disabled")
            frontend_url = settings.FRONTEND_URL or "/"
            return RedirectResponse(f"{frontend_url}?oauth_disabled=true")

        # Exchange code for credentials
        credentials = google_oauth.exchange_code(code)

        # Store credentials in session
        # In a real implementation, this would use a secure session store
        # or generate a JWT token
        request.session["credentials"] = json.dumps(credentials)

        # Redirect to frontend application
        frontend_url = settings.FRONTEND_URL or "/"
        return RedirectResponse(frontend_url)
    except HTTPException:
        # Pass through HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Failed to complete authentication: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete authentication: {str(e)}",
        )


@router.get("/status")
async def auth_status(request: Request) -> Dict[str, Any]:
    """Get current authentication status."""
    # Check if OAuth is disabled
    if GOOGLE_AUTH_DISABLED:
        return {
            "authenticated": False,
            "oauth_disabled": True,
            "message": "OAuth authentication is disabled for this deployment",
        }

    # Check for credentials in session
    credentials_str = request.session.get("credentials")
    if not credentials_str:
        return {"authenticated": False}

    return {"authenticated": True}


@router.get("/logout")
async def logout(request: Request):
    """Log out the current user by clearing the session."""
    # Clear session
    request.session.clear()

    return {"success": True, "message": "Logged out successfully"}
