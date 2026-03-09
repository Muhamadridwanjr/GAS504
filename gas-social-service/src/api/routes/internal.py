from fastapi import APIRouter, Depends
from src.api.dependencies import verify_internal_api_key
from src.api.models import SignalPostedPayload
from src.lib.logger import logger

router = APIRouter(prefix="/internal", tags=["Internal"])


@router.get("/ping", dependencies=[Depends(verify_internal_api_key)])
async def internal_ping():
    """Internal health/connectivity check for service mesh."""
    return {"status": "ok", "service": "gas-social-service"}


@router.post("/signal-posted", dependencies=[Depends(verify_internal_api_key)])
async def signal_posted(payload: SignalPostedPayload):
    """
    Called by gas-signal-service after an insider signal is persisted.
    Useful for triggering feed cache invalidation or additional fan-out logic.
    """
    logger.info(
        f"[Internal] Signal posted: signal_id={payload.signal_id} by user={payload.user_id}"
    )
    # Hook: cache invalidation, push to Redis queue, etc.
    return {
        "received": True,
        "signal_id": payload.signal_id,
        "user_id": payload.user_id,
    }
