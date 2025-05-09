"""
Utility functions for hashing.
"""
import hashlib
import hmac
from typing import Dict, Any


def generate_user_hash(user_info: Dict[str, Any], secret_key: str) -> str:
    """
    Generate a privacy-preserving hash for a user.
    
    Uses HMAC with SHA-256 and a server-side secret key to create a 
    deterministic but anonymous identifier for a user.
    
    Args:
        user_info: User information from Google OAuth (contains email, sub, etc.)
        secret_key: Server-side secret key
        
    Returns:
        Hexadecimal hash string
    """
    # Use Google's subject identifier (sub) as it's unique per user
    user_id = user_info.get("sub", "")
    
    if not user_id:
        raise ValueError("User info does not contain a subject identifier")
    
    # Create HMAC using server's secret key
    digest = hmac.new(
        key=secret_key.encode(),
        msg=user_id.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()
    
    return digest 