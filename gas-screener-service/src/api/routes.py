"""
API routes for gas-screener-service.
"""
from __future__ import annotations

from fastapi import APIRouter, Request
from src.api.models import ScreenerRequest, ScreenerResponse
from src.lib.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["Screener"])


@router.post("/screener", response_model=ScreenerResponse)
async def screener(request: ScreenerRequest, req: Request):
    """Perform parallel asset screening."""
    orchestrator = req.app.state.orchestrator
    result = await orchestrator.screen(request)
    return ScreenerResponse(**result)


@router.get("/symbols")
async def get_symbols():
    """Get default symbol list."""
    import json
    from src.config import settings
    return {"symbols": json.loads(settings.DEFAULT_SYMBOLS)}
