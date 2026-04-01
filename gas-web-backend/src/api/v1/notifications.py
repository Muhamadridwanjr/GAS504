"""
Notifications feed backed by Redis.
Notifications are stored as JSON strings in a Redis list: notifications:{user_id}
System-wide announcements live in: notifications:system
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from ...core.dependencies import get_current_user, get_current_user_info
import redis.asyncio as aioredis
import os
import json
from datetime import datetime, timezone

router = APIRouter(tags=["Notifications Feed"])

REDIS_URL = os.getenv("REDIS_URL", "redis://gas-redis:6379/0")
_redis = None

async def _get_redis():
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis


class MarkReadBody(BaseModel):
    notification_id: str


@router.get("/notifications")
async def get_notifications(
    limit: int = 20,
    user_info: dict = Depends(get_current_user_info),
):
    """Return user-specific + system notifications (newest first)."""
    user_id = user_info["user_id"]
    r = await _get_redis()

    # User-specific notifications (e.g. payment success, plan upgraded, credit award)
    user_key = f"notifications:{user_id}"
    system_key = "notifications:system"

    raw_user   = await r.lrange(user_key,   0, limit - 1)
    raw_system = await r.lrange(system_key, 0, 4)  # max 5 system notifs

    items = []
    for raw in raw_user + raw_system:
        try:
            items.append(json.loads(raw))
        except Exception:
            pass

    # Sort by timestamp descending
    items.sort(key=lambda x: x.get("ts", ""), reverse=True)

    # Compute unread count
    unread = sum(1 for n in items if not n.get("read", False))

    return {"notifications": items[:limit], "unread": unread, "total": len(items)}


@router.post("/notifications/mark-read")
async def mark_notification_read(
    body: MarkReadBody,
    user_info: dict = Depends(get_current_user_info),
):
    """Mark a notification as read (updates in-place in Redis list)."""
    user_id = user_info["user_id"]
    r = await _get_redis()
    user_key = f"notifications:{user_id}"

    raw_list = await r.lrange(user_key, 0, -1)
    updated = False
    for i, raw in enumerate(raw_list):
        try:
            obj = json.loads(raw)
            if obj.get("id") == body.notification_id:
                obj["read"] = True
                await r.lset(user_key, i, json.dumps(obj))
                updated = True
                break
        except Exception:
            pass

    return {"marked": updated, "notification_id": body.notification_id}


@router.post("/notifications/mark-all-read")
async def mark_all_read(user_info: dict = Depends(get_current_user_info)):
    """Mark all user notifications as read."""
    user_id = user_info["user_id"]
    r = await _get_redis()
    user_key = f"notifications:{user_id}"

    raw_list = await r.lrange(user_key, 0, -1)
    for i, raw in enumerate(raw_list):
        try:
            obj = json.loads(raw)
            if not obj.get("read"):
                obj["read"] = True
                await r.lset(user_key, i, json.dumps(obj))
        except Exception:
            pass

    return {"marked_all": True}


@router.delete("/notifications/{notification_id}")
async def delete_notification(
    notification_id: str,
    user_info: dict = Depends(get_current_user_info),
):
    """Delete a specific notification."""
    user_id = user_info["user_id"]
    r = await _get_redis()
    user_key = f"notifications:{user_id}"

    raw_list = await r.lrange(user_key, 0, -1)
    for raw in raw_list:
        try:
            obj = json.loads(raw)
            if obj.get("id") == notification_id:
                await r.lrem(user_key, 1, raw)
                return {"deleted": True}
        except Exception:
            pass

    raise HTTPException(status_code=404, detail="Notification not found")
