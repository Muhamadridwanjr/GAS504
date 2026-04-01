"""
TCG (Trading Card Game) Integration — reads real level/XP from Redis.
Cards stored per user in: tcg:{user_id}:cards (list of JSON)
Equipped card: tcg:{user_id}:equipped (string card_id)
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from ...core.dependencies import get_current_user, get_current_user_info
import redis.asyncio as aioredis
import os
import json

router = APIRouter(tags=["TCG Integration"])

REDIS_URL = os.getenv("REDIS_URL", "redis://gas-redis:6379/0")
_redis = None

async def _get_redis():
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis

LEVEL_DEFINITIONS = [
    {"level": 1, "xp_required": 0},
    {"level": 2, "xp_required": 100},
    {"level": 3, "xp_required": 300},
    {"level": 4, "xp_required": 600},
    {"level": 5, "xp_required": 1000},
    {"level": 6, "xp_required": 1500},
    {"level": 7, "xp_required": 2200},
    {"level": 8, "xp_required": 3000},
    {"level": 9, "xp_required": 4000},
    {"level": 10, "xp_required": 5500},
]

def _compute_level(xp: int) -> int:
    level = 1
    for ld in LEVEL_DEFINITIONS:
        if xp >= ld["xp_required"]:
            level = ld["level"]
    return min(level, 10)


class EquipBody(BaseModel):
    card_id: str


@router.get("/profile")
async def get_tcg_profile(user_info: dict = Depends(get_current_user_info)):
    """Get TCG profile using real level/XP from Redis."""
    user_id = user_info["user_id"]
    r = await _get_redis()

    xp = int(await r.get(f"user:{user_id}:xp") or 0)
    level = _compute_level(xp)

    raw_cards = await r.lrange(f"tcg:{user_id}:cards", 0, -1)
    cards = []
    for raw in raw_cards:
        try:
            cards.append(json.loads(raw))
        except Exception:
            pass

    equipped_id = await r.get(f"tcg:{user_id}:equipped")
    equipped_card = next((c for c in cards if c.get("id") == equipped_id), None)

    return {
        "level": level,
        "xp": xp,
        "collection_count": len(cards),
        "equipped_card": equipped_card,
        "user_id": user_id,
    }


@router.get("/cards")
async def get_tcg_cards(user_info: dict = Depends(get_current_user_info)):
    """List all TCG cards owned by the user."""
    user_id = user_info["user_id"]
    r = await _get_redis()

    raw_cards = await r.lrange(f"tcg:{user_id}:cards", 0, -1)
    cards = []
    equipped_id = await r.get(f"tcg:{user_id}:equipped")
    for raw in raw_cards:
        try:
            card = json.loads(raw)
            card["equipped"] = (card.get("id") == equipped_id)
            cards.append(card)
        except Exception:
            pass

    return {"cards": cards, "total": len(cards)}


@router.post("/equip")
async def equip_card(body: EquipBody, user_info: dict = Depends(get_current_user_info)):
    """Equip a card by ID."""
    user_id = user_info["user_id"]
    r = await _get_redis()

    # Verify card exists in user's collection
    raw_cards = await r.lrange(f"tcg:{user_id}:cards", 0, -1)
    found = False
    for raw in raw_cards:
        try:
            card = json.loads(raw)
            if card.get("id") == body.card_id:
                found = True
                break
        except Exception:
            pass

    if not found:
        raise HTTPException(status_code=404, detail="Card not found in your collection")

    await r.set(f"tcg:{user_id}:equipped", body.card_id)
    return {"message": "Card equipped successfully", "card_id": body.card_id}
