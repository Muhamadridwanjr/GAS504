"""Chart data orchestrator — merges OHLC + indicators + SMC."""
import asyncio
from src.clients.mt5_data_client import MT5DataClient
from src.clients.indicator_client import IndicatorClient
from src.clients.smc_client import SMCClient
from src.cache.redis_cache import RedisCache
from src.lib.utils import hash_key
from src.lib.logger import get_logger
logger = get_logger(__name__)

class ChartOrchestrator:
    def __init__(self, cache: RedisCache):
        self.cache = cache
        self.mt5 = MT5DataClient()
        self.indicator = IndicatorClient()
        self.smc = SMCClient()

    async def get_chart_data(self, symbol, timeframe, from_ts=None, to_ts=None, count=None,
                             indicators=None, include_smc=False):
        ck = f"chart:{hash_key(symbol, timeframe, str(from_ts), str(to_ts), str(count), str(indicators))}"
        cached = await self.cache.get(ck)
        if cached: return cached

        # Parallel fetch
        tasks = [self.mt5.get_ohlc(symbol, timeframe, from_ts, to_ts, count)]
        if indicators:
            tasks.append(self.indicator.calculate(symbol, timeframe, indicators))
        if include_smc:
            tasks.append(self.smc.detect(symbol, timeframe))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        ohlc = results[0] if not isinstance(results[0], Exception) else []
        ind_data = {}
        smc_data = {}
        idx = 1
        if indicators:
            ind_data = results[idx] if not isinstance(results[idx], Exception) else {}
            idx += 1
        if include_smc:
            smc_data = results[idx] if not isinstance(results[idx], Exception) else {}

        response = {"symbol": symbol, "timeframe": timeframe, "data": ohlc, "indicators": ind_data, "smc": smc_data}
        await self.cache.set(ck, response)
        return response
