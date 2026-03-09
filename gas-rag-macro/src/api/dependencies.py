"""
FastAPI dependencies for gas-rag-macro.
"""
from fastapi import Header, HTTPException


async def get_user_id(x_user_id: str = Header(default="")) -> str:
    """Extract user ID from X-User-ID header (injected by gateway)."""
    return x_user_id


async def get_request_id(x_request_id: str = Header(default="")) -> str:
    """Extract optional request ID for tracing."""
    return x_request_id
