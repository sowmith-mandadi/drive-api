"""
Authentication utilities for Google OAuth.
"""
import json
import logging
import os
from typing import Any, Dict

from fastapi import HTTPException, Request, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

from app.core.config import settings

# Setup logging
logger = logging.getLogger(__name__)

# Check if Google Auth is disabled
GOOGLE_AUTH_DISABLED = os.environ.get("GOOGLE_AUTH_DISABLED", "false").lower() == "true"

# OAuth2 scheme for authorization
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://accounts.google.com/o/oauth2/auth",
    tokenUrl="https://oauth2.googleapis.com/token",
    scopes={
        "https://www.googleapis.com/auth/drive.readonly": "Read files from Google Drive",
        "https://www.googleapis.com/auth/drive.metadata.readonly": "Read metadata of files from Google Drive",
    },
)


class GoogleOAuth:
    """Google OAuth authentication helper."""

    def __init__(self):
        """Initialize the Google OAuth helper."""
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI
        self.scopes = settings.GOOGLE_DRIVE_SCOPES
        self.auth_disabled = GOOGLE_AUTH_DISABLED

        # Check if credentials are available
        if self.auth_disabled:
            logger.warning("Google OAuth is disabled by configuration")
        elif not self.client_id or not self.client_secret:
            logger.warning("Google OAuth credentials not configured")

    def get_authorization_url(self) -> str:
        """Get the Google OAuth authorization URL.

        Returns:
            Authorization URL.

        Raises:
            HTTPException: If OAuth is disabled or credentials are not configured.
        """
        try:
            if self.auth_disabled:
                logger.warning("Attempted to get auth URL while OAuth is disabled")
                raise HTTPException(
                    status_code=status.HTTP_501_NOT_IMPLEMENTED,
                    detail="Google OAuth authentication is disabled",
                )

            if not self.client_id or not self.client_secret:
                logger.error("Cannot generate auth URL: OAuth credentials not configured")
                raise HTTPException(
                    status_code=status.HTTP_501_NOT_IMPLEMENTED,
                    detail="Google OAuth credentials are not configured",
                )

            # Create flow instance
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri],
                    }
                },
                scopes=self.scopes,
            )

            # Set redirect URI
            flow.redirect_uri = self.redirect_uri

            # Generate authorization URL
            authorization_url, _ = flow.authorization_url(
                access_type="offline", include_granted_scopes="true", prompt="consent"
            )

            return authorization_url
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to generate authorization URL: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate authorization URL: {str(e)}",
            )

    def exchange_code(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for credentials.

        Args:
            code: Authorization code from Google.

        Returns:
            Credentials dictionary.

        Raises:
            HTTPException: If OAuth is disabled or credentials are not configured.
        """
        try:
            if self.auth_disabled:
                logger.warning("Attempted to exchange code while OAuth is disabled")
                raise HTTPException(
                    status_code=status.HTTP_501_NOT_IMPLEMENTED,
                    detail="Google OAuth authentication is disabled",
                )

            if not self.client_id or not self.client_secret:
                logger.error("Cannot exchange code: OAuth credentials not configured")
                raise HTTPException(
                    status_code=status.HTTP_501_NOT_IMPLEMENTED,
                    detail="Google OAuth credentials are not configured",
                )

            # Create flow instance
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri],
                    }
                },
                scopes=self.scopes,
            )

            # Set redirect URI
            flow.redirect_uri = self.redirect_uri

            # Exchange code for credentials
            flow.fetch_token(code=code)

            # Get credentials
            credentials = flow.credentials

            # Return credentials as dictionary
            return {
                "token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scopes": credentials.scopes,
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to exchange code for credentials: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to exchange code for credentials: {str(e)}",
            )

    def refresh_credentials(self, credentials_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Refresh credentials if expired.

        Args:
            credentials_dict: Credentials dictionary.

        Returns:
            Refreshed credentials dictionary.

        Raises:
            HTTPException: If OAuth is disabled or credentials are not configured.
        """
        try:
            if self.auth_disabled:
                logger.warning("Attempted to refresh credentials while OAuth is disabled")
                raise HTTPException(
                    status_code=status.HTTP_501_NOT_IMPLEMENTED,
                    detail="Google OAuth authentication is disabled",
                )

            if not self.client_id or not self.client_secret:
                logger.error("Cannot refresh credentials: OAuth credentials not configured")
                raise HTTPException(
                    status_code=status.HTTP_501_NOT_IMPLEMENTED,
                    detail="Google OAuth credentials are not configured",
                )

            # Create credentials object
            credentials = Credentials(
                token=credentials_dict.get("token"),
                refresh_token=credentials_dict.get("refresh_token"),
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=self.scopes,
            )

            # Refresh if expired
            if credentials.expired:
                credentials.refresh(GoogleRequest())

                # Update dictionary
                credentials_dict["token"] = credentials.token

            return credentials_dict
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to refresh credentials: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to refresh credentials: {str(e)}",
            )


# OAuth helper instance
google_oauth = GoogleOAuth()


async def get_current_user_credentials(request: Request) -> Dict[str, Any]:
    """Get the current user's credentials from session or cookie.

    In a real implementation, this would retrieve the user's credentials
    from a secure session store or a JWT token. For simplicity, this
    mock implementation uses the request session.

    Args:
        request: FastAPI request object.

    Returns:
        User credentials dictionary.

    Raises:
        HTTPException: If user is not authenticated.
    """
    try:
        # If auth is disabled, return mock credentials
        if GOOGLE_AUTH_DISABLED:
            logger.info("OAuth is disabled, using mock credentials")
            return {
                "token": "mock_token",
                "refresh_token": "mock_refresh_token",
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": "mock_client_id",
                "client_secret": "mock_client_secret",
                "scopes": settings.GOOGLE_DRIVE_SCOPES,
                "mock": True,
            }

        # For development, use mock credentials if no real credentials are configured
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            logger.warning("Using mock credentials for development")
            return {
                "token": "mock_token",
                "refresh_token": "mock_refresh_token",
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": "mock_client_id",
                "client_secret": "mock_client_secret",
                "scopes": settings.GOOGLE_DRIVE_SCOPES,
                "mock": True,
            }

        # Get credentials from session
        # In a real implementation, this would use a secure session store
        credentials_str = request.session.get("credentials")
        if not credentials_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Parse credentials
        credentials_dict = json.loads(credentials_str)

        # Refresh if expired
        try:
            credentials_dict = google_oauth.refresh_credentials(credentials_dict)
            # Update session with refreshed credentials
            request.session["credentials"] = json.dumps(credentials_dict)
        except Exception as e:
            logger.error(f"Failed to refresh credentials: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return credentials_dict
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication error",
            headers={"WWW-Authenticate": "Bearer"},
        )
