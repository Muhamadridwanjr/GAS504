from typing import Optional
from fastapi import Header, HTTPException, Depends
from src.config import settings


async def get_current_user_id(
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
) -> str:
    """
    Extract and validate the authenticated user ID from gateway-injected header.
    The gas-gateway-api sets this header after JWT validation.
    """
    if not x_user_id:
        raise HTTPException(
            status_code=401,
            detail="Missing X-User-ID header. Request must go through gas-gateway-api.",
        )
    return x_user_id


async def verify_internal_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
) -> None:
    """
    Verify the internal API key for inter-service communication.
    Used only on /internal/* endpoints.
    """
    if not x_api_key or x_api_key != settings.INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing internal API key.")
