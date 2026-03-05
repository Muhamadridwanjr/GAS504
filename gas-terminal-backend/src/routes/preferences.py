"""
GET/POST /terminal/user/preferences – User preferences.
Uses in-memory store as fallback when user-service is unavailable.
"""
from fastapi import APIRouter, Request
from src.config import settings
from src.services.client import fetch_json

router = APIRouter()

# Simple in-memory store (keyed by X-User-ID header)
_prefs_store: dict[str, dict] = {}

DEFAULT_PREFS = {
    "notifications": True,
    "sound": True,
    "autoRefresh": True,
    "darkMode": True,
    "favorites": ["XAUUSD", "BTCUSD"],
}


@router.get("/terminal/user/preferences")
async def get_preferences(request: Request):
    """Get user preferences."""
    user_id = request.headers.get("X-User-ID", "anonymous")

    # Try upstream user service first
    data = await fetch_json(f"{settings.USER_SERVICE_URL}/user/preferences", headers={"X-User-ID": user_id})
    if "error" not in data and isinstance(data, dict) and "preferences" in data:
        return {"status": "ok", "preferences": data["preferences"]}

    # Fallback to local store
    prefs = _prefs_store.get(user_id, DEFAULT_PREFS.copy())
    return {"status": "ok", "preferences": prefs}


@router.post("/terminal/user/preferences")
async def save_preferences(request: Request):
    """Save user preferences."""
    user_id = request.headers.get("X-User-ID", "anonymous")
    body = await request.json()

    # Try upstream
    data = await fetch_json(
        f"{settings.USER_SERVICE_URL}/user/preferences",
        method="POST",
        json_body=body,
        headers={"X-User-ID": user_id},
    )
    if "error" not in data:
        return {"status": "ok", "message": "Preferences saved"}

    # Fallback to local store
    _prefs_store[user_id] = body
    return {"status": "ok", "message": "Preferences saved locally"}
