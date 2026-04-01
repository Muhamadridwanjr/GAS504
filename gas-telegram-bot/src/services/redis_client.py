"""
Redis client shared across the bot.
Keys used:
  tg:link:{code}       → tg_user_id     (TTL 15 min — pending link codes)
  tg:bind:{tg_user_id} → gas_user_id    (permanent — linked accounts)
  user:{gas_user_id}:plan               → plan name
  user:{gas_user_id}:credits            → credit balance
  user:{gas_user_id}:xp                 → XP
  user:{gas_user_id}:booster            → booster badge name
"""
import redis.asyncio as aioredis
from src.config import settings

_redis = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis
