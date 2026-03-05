"""Business logic for fundamental data queries."""
from __future__ import annotations
from src.db.repositories.fundamental_repo import FundamentalRepo
from src.cache.redis_cache import RedisCache
from src.lib.utils import hash_key
from src.lib.logger import get_logger

logger = get_logger(__name__)

class DataService:
    def __init__(self, repo: FundamentalRepo, cache: RedisCache):
        self.repo = repo
        self.cache = cache

    async def get_data(self, symbol: str, indicator: str, from_time=None, to_time=None, limit=100):
        cache_key = f"fund:{hash_key(symbol, indicator, str(from_time), str(to_time), str(limit))}"
        cached = await self.cache.get(cache_key)
        if cached: return cached
        rows = await self.repo.get_data(symbol, indicator, from_time, to_time, limit)
        data = [{"time": r.time, "value": r.value, "unit": r.unit} for r in rows]
        result = {"symbol": symbol, "indicator": indicator, "data": data}
        await self.cache.set(cache_key, result)
        return result
