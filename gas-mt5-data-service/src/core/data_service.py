import json
from typing import List, Dict, Any, Optional
import time

from src.core.mt5_connector import MT5Connector
from src.cache.redis_cache import RedisCache
from src.lib.logger import logger
from src.config import settings

class DataService:
    def __init__(self):
        self.mt5_connector = MT5Connector()
        self.cache = RedisCache()

    def _generate_cache_key(self, symbol, timeframe, from_time, to_time, count):
        return f"ohlc:{symbol}:{timeframe}:{from_time}:{to_time}:{count}"

    async def get_historical_data(self, symbol: str, timeframe: str, from_time: Optional[int] = None, to_time: Optional[int] = None, count: Optional[int] = None, include_volume: bool = True) -> List[Dict[str, Any]]:
        cache_key = self._generate_cache_key(symbol, timeframe, from_time, to_time, count)
        
        # 1. Try Cache
        try:
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                logger.info(f"Cache hit for {cache_key}")
                data = json.loads(cached_data)
                if not include_volume:
                    for item in data:
                        item.pop("volume", None)
                return data
        except Exception as e:
            logger.error(f"Cache read error: {e}")

        # 2. Fetch from MT5
        logger.info(f"Cache miss for {cache_key}, fetching from MT5...")
        data = await self.mt5_connector.fetch_history(symbol, timeframe, from_time, to_time, count)

        # 3. Save to Cache
        if data:
            try:
                await self.cache.set(cache_key, json.dumps(data), expire=settings.CACHE_TTL)
            except Exception as e:
                logger.error(f"Cache write error: {e}")

        # Filter volume if needed
        if not include_volume:
            for item in data:
                item.pop("volume", None)

        return data
