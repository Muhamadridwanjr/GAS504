"""
API dependencies – extracts user/auth context from request headers.
"""
from fastapi import Header, HTTPException, status
from src.config import settings


async def get_user_id(x_user_id: str | None = Header(default=None)) -> str | None:
    """Extract user ID from X-User-ID header (set by gateway)."""
    return x_user_id


async def verify_internal_key(
    x_api_key: str | None = Header(default=None),
) -> None:
    """Verify internal API key for admin/internal endpoints."""
    if settings.INTERNAL_API_KEY and x_api_key != settings.INTERNAL_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing internal API key.",
        )
