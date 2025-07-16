from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
import os
from dotenv import load_dotenv

load_dotenv()

# Create API key header without auto_error to avoid Pydantic constraint issues
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


def ensure_valid_api_key(api_key: str = Security(api_key_header)):
    def check_api_key(key: str) -> bool:
        if not key:
            return False
        valid_keys = os.environ.get("API_KEYS", "").split(",")
        return key in valid_keys and key != ""

    if not api_key or not check_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API key. Use x-api-key header.",
        )
