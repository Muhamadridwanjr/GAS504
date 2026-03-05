"""
Parallel executor — calls engines concurrently for each symbol.
"""
from __future__ import annotations
import asyncio
from typing import Any

from src.clients.indicator_client import IndicatorClient
from src.clients.smc_client import SMCClient
from src.api.models import ScreenerCondition
from src.config import settings
from src.lib.logger import get_logger

logger = get_logger(__name__)


async def fetch_symbol_data(
    symbol: str,
    timeframe: str,
    conditions: list[ScreenerCondition],
    semaphore: asyncio.Semaphore,
) -> dict[str, Any]:
    """Fetch indicator and SMC data for a single symbol."""
    async with semaphore:
        indicator_client = IndicatorClient()
        smc_client = SMCClient()

        # Build indicator list from conditions
        ind_requests = [
            {"name": c.name, "period": c.period}
            for c in conditions if c.type == "indicator"
        ]

        # Parallel calls to indicator engine + SMC engine
        ind_task = indicator_client.calculate(symbol, timeframe, ind_requests) if ind_requests else asyncio.coroutine(lambda: {})()
        smc_task = smc_client.detect(symbol, timeframe)

        results = await asyncio.gather(ind_task, smc_task, return_exceptions=True)

        indicators = results[0] if not isinstance(results[0], Exception) else {}
        smc = results[1] if not isinstance(results[1], Exception) else {}

        return {
            "symbol": symbol,
            "indicators": indicators,
            "smc": smc,
        }


async def execute_parallel(
    symbols: list[str],
    timeframe: str,
    conditions: list[ScreenerCondition],
) -> list[dict[str, Any]]:
    """Execute data fetching for all symbols in parallel with concurrency limit."""
    semaphore = asyncio.Semaphore(settings.CONCURRENCY_LIMIT)

    tasks = [
        fetch_symbol_data(symbol, timeframe, conditions, semaphore)
        for symbol in symbols
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    valid_results = []
    for r in results:
        if isinstance(r, Exception):
            logger.error("Parallel task failed: %s", r)
        else:
            valid_results.append(r)

    logger.info("Fetched data for %d / %d symbols", len(valid_results), len(symbols))
    return valid_results
