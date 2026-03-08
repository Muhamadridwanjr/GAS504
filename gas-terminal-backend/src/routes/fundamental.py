"""
Proxy routes for fundamental macro data → gas-fundamental-data-service.
"""
from fastapi import APIRouter, Request
from src.config import settings
from src.services.client import fetch_json

router = APIRouter()

_INTERNAL_HEADERS = {"X-Internal-Key": "gas-internal-secret-key"}


@router.get("/terminal/fundamental/macro")
async def get_macro_dashboard(request: Request):
    """Proxy to gas-fundamental-data-service /macro/dashboard."""
    data = await fetch_json(
        f"{settings.FUNDAMENTAL_DATA_URL}/macro/dashboard",
        headers=_INTERNAL_HEADERS,
    )
    return data


@router.post("/terminal/fundamental/refresh")
async def trigger_refresh(request: Request):
    """Proxy refresh trigger to fundamental service."""
    data = await fetch_json(
        f"{settings.FUNDAMENTAL_DATA_URL}/macro/refresh",
        method="POST",
        headers=_INTERNAL_HEADERS,
    )
    return data
