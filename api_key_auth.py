from fastapi import HTTPException, status, Request
import os
from dotenv import load_dotenv

load_dotenv()


def ensure_valid_api_key(request: Request):
    """Simple API key validation using request headers"""
    api_key = request.headers.get("x-api-key") or request.headers.get("authorization", "").replace("Bearer ", "")
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing API key. Use x-api-key header or Authorization: Bearer <key>",
        )
    
    valid_keys = os.environ.get("API_KEYS", "").split(",")
    if api_key not in valid_keys or not api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )
    
    return api_key
