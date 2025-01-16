from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from typing import Optional

from app.core.config import get_settings

settings = get_settings()

# Create API key header scheme
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

async def verify_token(api_key: Optional[str] = Security(api_key_header)) -> bool:
    """Verify the API token from the Authorization header"""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing"
        )
        
    scheme, _, token = api_key.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header must start with Bearer"
        )
        
    if not token or token != settings.API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
        
    return True