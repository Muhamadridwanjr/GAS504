"""
GAS Bot — Redis Session State Manager
Stores per-user flow state so multi-user interactions don't collide.
Key: user:{tg_id}:state  TTL: 10 minutes
"""
import json
from typing import Any, Optional
from src.services.redis_client import get_redis

STATE_TTL = 600  # 10 minutes


async def set_state(tg_user_id: int, key: str, value: Any) -> None:
    r = await get_redis()
    raw = await r.get(f"user:{tg_user_id}:state") or "{}"
    state = json.loads(raw)
    state[key] = value
    await r.set(f"user:{tg_user_id}:state", json.dumps(state), ex=STATE_TTL)


async def get_state(tg_user_id: int, key: str, default: Any = None) -> Any:
    r = await get_redis()
    raw = await r.get(f"user:{tg_user_id}:state") or "{}"
    state = json.loads(raw)
    return state.get(key, default)


async def get_full_state(tg_user_id: int) -> dict:
    r = await get_redis()
    raw = await r.get(f"user:{tg_user_id}:state") or "{}"
    return json.loads(raw)


async def clear_state(tg_user_id: int) -> None:
    r = await get_redis()
    await r.delete(f"user:{tg_user_id}:state")


async def update_state(tg_user_id: int, updates: dict) -> None:
    r = await get_redis()
    raw = await r.get(f"user:{tg_user_id}:state") or "{}"
    state = json.loads(raw)
    state.update(updates)
    await r.set(f"user:{tg_user_id}:state", json.dumps(state), ex=STATE_TTL)
