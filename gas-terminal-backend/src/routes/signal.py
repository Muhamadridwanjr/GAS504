"""
GET /terminal/signal/latest – Latest trading signal for a pair.
Real data only — no mock/random generation.
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Query
from src.config import settings
from src.services.client import fetch_json

router = APIRouter()


@router.get("/terminal/signal/latest")
async def get_latest_signal(pair: str = Query("XAUUSD")):
    """Get latest signal from GAS engine. Real data only."""
    orch_url = f"{settings.ENGINE_ORCHESTRATOR_URL}/signal/orchestrated"
    data = await fetch_json(orch_url, params={"pair": pair}, timeout=10.0)

    if "error" in data:
        sig_url = f"{settings.SIGNAL_SERVICE_URL}/signal/latest"
        data = await fetch_json(sig_url, params={"pair": pair}, timeout=8.0)

    if "error" in data:
        return {
            "status": "unavailable",
            "signal": None,
            "message": "Engine sinyal sedang tidak tersedia.",
            "timestamp": int(datetime.now(timezone.utc).timestamp()),
        }

    if "status" in data and "signal" in data:
        return data

    return {"status": "ok", "signal": data}
