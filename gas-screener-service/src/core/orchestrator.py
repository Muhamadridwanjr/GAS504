"""
Screener orchestrator — ties parallel execution, condition evaluation, and caching together.
"""
from __future__ import annotations
import json, time
from typing import Any

from src.api.models import ScreenerRequest, ScreenerResult
from src.core.parallel_executor import execute_parallel
from src.core.condition_evaluator import evaluate_all
from src.cache.redis_cache import RedisCache
from src.config import settings
from src.lib.utils import hash_key
from src.lib.logger import get_logger

logger = get_logger(__name__)


class ScreenerOrchestrator:
    def __init__(self, cache: RedisCache):
        self.cache = cache

    async def screen(self, request: ScreenerRequest) -> dict[str, Any]:
        """Run the full screening pipeline."""
        start = time.monotonic()

        symbols = request.symbols
        if not symbols:
            symbols = json.loads(settings.DEFAULT_SYMBOLS)

        # Check cache
        cache_key = f"screener:{hash_key(json.dumps(symbols), request.timeframe, json.dumps([c.model_dump() for c in request.conditions], default=str), request.logic)}"
        cached = await self.cache.get(cache_key)
        if cached:
            cached["metadata"]["cache_hit"] = True
            return cached

        # Parallel data fetch
        raw_results = await execute_parallel(symbols, request.timeframe, request.conditions)

        # Filter
        passed: list[ScreenerResult] = []
        for r in raw_results:
            if evaluate_all(request.conditions, r.get("indicators", {}), r.get("smc", {}), request.logic):
                passed.append(ScreenerResult(
                    symbol=r["symbol"],
                    indicators=r.get("indicators", {}) if request.include_metadata else {},
                    smc=r.get("smc", {}) if request.include_metadata else {},
                ))

        elapsed_ms = round((time.monotonic() - start) * 1000)
        response = {
            "total": len(passed),
            "results": [p.model_dump() for p in passed],
            "metadata": {
                "processing_time_ms": elapsed_ms,
                "cache_hit": False,
            },
        }

        # Store in cache
        await self.cache.set(cache_key, response)

        logger.info("Screened %d symbols → %d passed (%dms)", len(symbols), len(passed), elapsed_ms)
        return response
