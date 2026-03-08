"""
GET /terminal/signal/latest – Latest trading signal for a pair.
"""
import random
from fastapi import APIRouter, Query
from src.config import settings
from src.services.client import fetch_json

router = APIRouter()

@router.get("/terminal/signal/latest")
async def get_latest_signal(pair: str = Query("XAUUSD")):
    """Get latest signal orchestrated across the whole GAS ecosystem."""
    # First, try to fetch from the newly implemented orchestrator logic
    orch_url = f"{settings.ENGINE_ORCHESTRATOR_URL}/signal/orchestrated"
    data = await fetch_json(orch_url, params={"pair": pair})
    
    if "error" in data:
        # Fallback to older direct signal service if orchestrator is totally offline
        sig_url = f"{settings.SIGNAL_SERVICE_URL}/signal/latest"
        data = await fetch_json(sig_url, params={"pair": pair})
    
    # Extract inner data response format from orchestrator if ok
    if "status" in data and "signal" in data:
        return data
    
    return {"status": "ok", "signal": data}
