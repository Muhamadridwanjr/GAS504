"""Calendar query logic."""
from src.db.repositories.event_repo import EventRepo
from src.cache.redis_cache import RedisCache
from src.lib.utils import hash_key

class CalendarService:
    def __init__(self, repo: EventRepo, cache: RedisCache):
        self.repo = repo; self.cache = cache

    async def get_events(self, country=None, importance=None, from_date=None, to_date=None, limit=100):
        ck = f"cal:{hash_key(str(country),str(importance),str(from_date),str(to_date))}"
        cached = await self.cache.get(ck)
        if cached: return cached
        rows = await self.repo.get_events(country, importance, from_date, to_date, limit)
        data = [{"id": r.id, "provider": r.provider, "title": r.title, "country": r.country,
                 "importance": r.importance, "time_utc": str(r.time_utc),
                 "actual_value": r.actual_value, "forecast_value": r.forecast_value,
                 "previous_value": r.previous_value, "unit": r.unit} for r in rows]
        result = {"total": len(data), "data": data}
        await self.cache.set(ck, result)
        return result
