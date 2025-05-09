"""
Dependencies for FastAPI.
"""
from typing import Dict, Any

from fastapi import Depends, HTTPException, Request, status

from app.core.auth import get_current_user_credentials


async def get_current_user_hash(
    credentials: Dict[str, Any] = Depends(get_current_user_credentials)
) -> str:
    """Get the current user's hash identifier."""
    user_hash = credentials.get("user_hash")
    
    if not user_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_hash 