"""
Economic calendar fetcher for gas-rag-macro.

Uses ForexFactory RSS as the primary source for economic event data.
Can be extended to support paid APIs (e.g., Investing.com via RapidAPI).
"""
from __future__ import annotations
import asyncio

import feedparser

from src.lib.logger import get_logger

logger = get_logger(__name__)

# Symbol → currency codes for calendar filtering
SYMBOL_CURRENCIES: dict[str, list[str]] = {
    "XAUUSD": ["USD"],
    "EURUSD": ["EUR", "USD"],
    "USDJPY": ["USD", "JPY"],
    "GBPUSD": ["GBP", "USD"],
    "BTCUSD": ["USD"],
    "USOIL": ["USD"],
    "US30": ["USD"],
    "NAS100": ["USD"],
}

# High-impact keywords to flag
HIGH_IMPACT_KEYWORDS = [
    "CPI", "NFP", "GDP", "fomc", "Fed", "interest rate", "inflation",
    "unemployment", "retail sales", "PMI", "payroll", "rate decision",
]


class ForexFactoryCalendarFetcher:
    """
    Fetches economic calendar events from ForexFactory RSS.
    RSS URL: https://nfs.faireconomy.media/ff_calendar_thisweek.json
    """

    CALENDAR_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

    async def fetch(self, symbol: str) -> list[dict]:
        """
        Fetch this week's economic calendar events, filtered by symbol currencies.

        Args:
            symbol: Trading symbol for currency filtering.

        Returns:
            List of event dicts.
        """
        import httpx

        currencies = SYMBOL_CURRENCIES.get(symbol.upper(), ["USD"])

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.CALENDAR_URL)
                response.raise_for_status()
                data = response.json()
        except Exception as exc:
            logger.warning("calendar.forexfactory.error", error=str(exc))
            return []

        events = []
        for ev in data:
            if ev.get("country") not in currencies and not any(
                c in str(ev.get("title", "")).upper() for c in currencies
            ):
                currency = ev.get("country", "")
                if currency not in currencies:
                    continue

            title = ev.get("title", "")
            impact_str = ev.get("impact", "Low")
            impact = "high" if impact_str == "High" else ("medium" if impact_str == "Medium" else "low")

            events.append({
                "event": title,
                "date": ev.get("date", ""),
                "forecast": ev.get("forecast", None),
                "previous": ev.get("previous", None),
                "impact": impact,
                "currency": ev.get("country", ""),
            })

        # Sort by impact (high first)
        impact_order = {"high": 0, "medium": 1, "low": 2}
        events.sort(key=lambda e: impact_order.get(e["impact"], 2))
        logger.info("calendar.fetched", count=len(events), symbol=symbol)
        return events


class CalendarFetcher:
    """
    Aggregated economic calendar fetcher.
    Currently uses ForexFactory; extensible to other providers.
    """

    def __init__(self):
        self._ff = ForexFactoryCalendarFetcher()

    async def fetch(self, symbol: str) -> list[dict]:
        """
        Fetch upcoming economic calendar events relevant to the symbol.

        Args:
            symbol: Trading symbol.

        Returns:
            List of event dicts sorted by impact (high first).
        """
        return await self._ff.fetch(symbol)
