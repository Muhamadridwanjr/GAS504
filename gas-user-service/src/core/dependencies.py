from fastapi import Request, Depends, HTTPException, status
from src.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

async def get_current_user_id(request: Request) -> UUID:
    """
    Extracts user_id from request.state.user.
    This state is expected to be populated by the API Gateway.
    """
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        # Fallback to header if needed (e.g. for testing or specific gateway setups)
        user_id = request.headers.get("X-User-Id")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in request state or headers"
        )
    try:
        return UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid User ID format"
        )

def verify_internal_api_key(request: Request):
    """
    Simple internal API key verification.
    In production, this should check against a secure store or env variable.
    """
    expected_key = "secret-internal-key" # Should be in settings
    api_key = request.headers.get("X-API-Key")
    if api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Internal API Key"
        )
