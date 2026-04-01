"""
AI Trade Journal — Redis-backed CRUD.
Journal entries stored as: journal:{user_id}:{entry_id} (Hash)
Index of entry IDs: journal:{user_id}:index (Sorted Set, score = timestamp)
MT5 auto-log webhook: stores trade event and returns success
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from ...core.dependencies import get_current_user, get_current_user_info
import redis.asyncio as aioredis
import os
import json
import uuid
from datetime import datetime, timezone

router = APIRouter(tags=["Journal"])

REDIS_URL = os.getenv("REDIS_URL", "redis://gas-redis:6379/0")
_redis = None

async def _get_redis():
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis


class JournalEntry(BaseModel):
    pair: Optional[str] = "XAUUSD"
    direction: Optional[str] = ""          # BUY | SELL
    entry_price: Optional[float] = None
    exit_price: Optional[float] = None
    sl: Optional[float] = None
    tp: Optional[float] = None
    lot: Optional[float] = None
    pnl: Optional[float] = None
    emotion: Optional[str] = ""            # calm | greedy | fearful | confident
    notes: Optional[str] = ""
    session: Optional[str] = ""
    tags: Optional[List[str]] = []
    image_url: Optional[str] = ""


class MT5WebhookPayload(BaseModel):
    ticket: Optional[int] = None
    pair: Optional[str] = ""
    direction: Optional[str] = ""
    entry_price: Optional[float] = None
    exit_price: Optional[float] = None
    lot: Optional[float] = None
    pnl: Optional[float] = None
    open_time: Optional[str] = ""
    close_time: Optional[str] = ""
    comment: Optional[str] = ""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _ts_score() -> float:
    return datetime.now(timezone.utc).timestamp()


@router.get("/")
async def list_journals(
    limit: int = 20,
    offset: int = 0,
    user_info: dict = Depends(get_current_user_info),
):
    """List journal entries, newest first."""
    user_id = user_info["user_id"]
    r = await _get_redis()
    index_key = f"journal:{user_id}:index"

    # Sorted set: score=timestamp, value=entry_id. ZREVRANGE gives newest first.
    total = await r.zcard(index_key)
    entry_ids = await r.zrevrange(index_key, offset, offset + limit - 1)

    entries = []
    for eid in entry_ids:
        data = await r.hgetall(f"journal:{user_id}:{eid}")
        if data:
            # Parse JSON fields
            for field in ("tags",):
                if field in data:
                    try:
                        data[field] = json.loads(data[field])
                    except Exception:
                        data[field] = []
            entries.append(data)

    return {"entries": entries, "total": total, "offset": offset, "limit": limit}


@router.post("/")
async def create_journal(
    entry: JournalEntry,
    user_info: dict = Depends(get_current_user_info),
):
    """Create a new journal entry."""
    user_id = user_info["user_id"]
    r = await _get_redis()

    entry_id = str(uuid.uuid4())
    now = _now_iso()
    ts = _ts_score()

    data = {
        "id": entry_id,
        "user_id": user_id,
        "created_at": now,
        "updated_at": now,
        "pair": entry.pair or "",
        "direction": entry.direction or "",
        "entry_price": str(entry.entry_price or ""),
        "exit_price": str(entry.exit_price or ""),
        "sl": str(entry.sl or ""),
        "tp": str(entry.tp or ""),
        "lot": str(entry.lot or ""),
        "pnl": str(entry.pnl or ""),
        "emotion": entry.emotion or "",
        "notes": entry.notes or "",
        "session": entry.session or "",
        "tags": json.dumps(entry.tags or []),
        "image_url": entry.image_url or "",
        "source": "manual",
    }

    await r.hset(f"journal:{user_id}:{entry_id}", mapping=data)
    await r.zadd(f"journal:{user_id}:index", {entry_id: ts})
    # Keep at most 200 entries per user
    await r.zremrangebyrank(f"journal:{user_id}:index", 0, -201)

    # Award XP for journal entry
    await r.incrby(f"user:{user_id}:xp", 20)

    # Update leaderboard: increment pnl score and trade count
    if entry.pnl is not None:
        await r.zadd("leaderboard:pnl",   {user_id: 0}, nx=True)  # ensure member exists
        await r.zincrby("leaderboard:pnl", entry.pnl, user_id)
    await r.zincrby("leaderboard:trades", 1, user_id)
    # Store username for leaderboard display
    real_username = user_info.get("username") or ""
    stored_username = await r.get(f"user:{user_id}:username")
    if real_username and (not stored_username or stored_username == user_id[:8]):
        await r.set(f"user:{user_id}:username", real_username, ex=86400 * 30)
    elif not stored_username:
        await r.set(f"user:{user_id}:username", user_id[:8], ex=86400 * 30)

    data["tags"] = entry.tags or []
    return {"message": "Journal entry created", "entry": data}


@router.get("/{entry_id}")
async def get_journal(entry_id: str, user_info: dict = Depends(get_current_user_info)):
    user_id = user_info["user_id"]
    r = await _get_redis()
    data = await r.hgetall(f"journal:{user_id}:{entry_id}")
    if not data:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    if "tags" in data:
        try:
            data["tags"] = json.loads(data["tags"])
        except Exception:
            data["tags"] = []
    return data


@router.put("/{entry_id}")
async def update_journal(
    entry_id: str,
    entry: JournalEntry,
    user_info: dict = Depends(get_current_user_info),
):
    user_id = user_info["user_id"]
    r = await _get_redis()
    key = f"journal:{user_id}:{entry_id}"
    existing = await r.hgetall(key)
    if not existing:
        raise HTTPException(status_code=404, detail="Journal entry not found")

    updates = {
        "updated_at": _now_iso(),
        "pair": entry.pair or existing.get("pair", ""),
        "direction": entry.direction or existing.get("direction", ""),
        "entry_price": str(entry.entry_price) if entry.entry_price is not None else existing.get("entry_price", ""),
        "exit_price": str(entry.exit_price) if entry.exit_price is not None else existing.get("exit_price", ""),
        "sl": str(entry.sl) if entry.sl is not None else existing.get("sl", ""),
        "tp": str(entry.tp) if entry.tp is not None else existing.get("tp", ""),
        "lot": str(entry.lot) if entry.lot is not None else existing.get("lot", ""),
        "pnl": str(entry.pnl) if entry.pnl is not None else existing.get("pnl", ""),
        "emotion": entry.emotion or existing.get("emotion", ""),
        "notes": entry.notes or existing.get("notes", ""),
        "session": entry.session or existing.get("session", ""),
        "tags": json.dumps(entry.tags) if entry.tags is not None else existing.get("tags", "[]"),
        "image_url": entry.image_url or existing.get("image_url", ""),
    }
    await r.hset(key, mapping=updates)
    return {"message": "Journal entry updated", "id": entry_id}


@router.delete("/{entry_id}")
async def delete_journal(entry_id: str, user_info: dict = Depends(get_current_user_info)):
    user_id = user_info["user_id"]
    r = await _get_redis()
    deleted = await r.delete(f"journal:{user_id}:{entry_id}")
    if not deleted:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    await r.zrem(f"journal:{user_id}:index", entry_id)
    return {"message": "Journal entry deleted", "id": entry_id}


@router.post("/mt5-webhook")
async def mt5_webhook(
    payload: MT5WebhookPayload,
    user_info: dict = Depends(get_current_user_info),
):
    """Auto-log trade from MT5 EA — Ultimate plan only."""
    user_id = user_info["user_id"]
    is_admin = user_info["is_admin"]
    r = await _get_redis()

    if not is_admin:
        user_plan = (await r.get(f"user:{user_id}:plan")) or "free"
        if user_plan != "ultimate":
            raise HTTPException(status_code=403, detail="Auto-log dari EA hanya tersedia di plan Ultimate.")

    entry_id = str(uuid.uuid4())
    now = _now_iso()
    ts = _ts_score()

    data = {
        "id": entry_id,
        "user_id": user_id,
        "created_at": now,
        "updated_at": now,
        "pair": payload.pair or "",
        "direction": payload.direction or "",
        "entry_price": str(payload.entry_price or ""),
        "exit_price": str(payload.exit_price or ""),
        "lot": str(payload.lot or ""),
        "pnl": str(payload.pnl or ""),
        "sl": "",
        "tp": "",
        "emotion": "",
        "notes": payload.comment or "Auto-logged from MT5 EA",
        "session": "",
        "tags": json.dumps(["auto-mt5"]),
        "image_url": "",
        "source": "mt5-ea",
        "ticket": str(payload.ticket or ""),
        "open_time": payload.open_time or "",
        "close_time": payload.close_time or "",
    }

    await r.hset(f"journal:{user_id}:{entry_id}", mapping=data)
    await r.zadd(f"journal:{user_id}:index", {entry_id: ts})
    # Award XP
    await r.incrby(f"user:{user_id}:xp", 20)

    return {"message": "Auto log from EA successful", "entry_id": entry_id, "ticket": payload.ticket}
