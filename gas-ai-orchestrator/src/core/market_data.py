"""
market_data.py — Fetches OHLCV from Redis ticks + macro context from datamacro.md
"""
import json
import os
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from src.config import settings
from src.lib.logger import setup_logger

logger = setup_logger(__name__)

# Path to datamacro.md (mounted into container or relative to repo root)
_MACRO_MD_PATHS = [
    "/data/datamacro.md",
    "/app/datamacro.md",
    os.path.join(os.path.dirname(__file__), "../../../../datamacro.md"),
]

# Pair → section keywords to extract from datamacro.md
PAIR_MACRO_KEYS = {
    "XAUUSD":  ["GOLD", "XAU", "NFP", "CPI", "FOMC", "Fed", "Treasury", "DXY"],
    "XAGUSD":  ["SILVER", "XAG", "ISM Manufacturing", "Industrial"],
    "EURUSD":  ["EUR", "Eurozone", "ECB", "HICP", "eurozone GDP"],
    "GBPUSD":  ["GBP", "UK", "BOE", "Britain", "Sterling"],
    "USDJPY":  ["JPY", "BOJ", "Japan", "yen", "USDJPY"],
    "GBPJPY":  ["GBP", "JPY", "BOJ", "BOE"],
    "BTCUSD":  ["BTC", "Bitcoin", "crypto", "ETF", "digital asset"],
    "ETHUSD":  ["ETH", "Ethereum", "crypto"],
    "NASDAQ":  ["NDQ", "NASDAQ", "tech", "SPX", "earnings", "VIX"],
    "US30":    ["DJI", "Dow", "SPX", "equities", "VIX"],
    "US500":   ["SPX", "S&P", "equities", "earnings"],
    "DXY":     ["DXY", "Dollar", "Fed", "NFP", "CPI"],
}


def _load_macro_md() -> str:
    for path in _MACRO_MD_PATHS:
        try:
            resolved = os.path.realpath(path)
            if os.path.exists(resolved):
                with open(resolved, "r") as f:
                    return f.read()
        except Exception:
            pass
    return ""


def _extract_macro_for_pair(pair: str, full_text: str) -> str:
    """Extract the most relevant paragraphs from datamacro.md for a given pair."""
    if not full_text:
        return ""

    pair_upper = pair.upper()
    base = pair_upper[:3]  # XAU, EUR, GBP, etc.
    keywords = PAIR_MACRO_KEYS.get(pair_upper, [base])

    # Split into sections by ## headers
    sections = re.split(r'\n(?=##)', full_text)
    scored: List[Tuple[int, str]] = []
    for section in sections:
        score = sum(1 for kw in keywords if kw.lower() in section.lower())
        if score > 0:
            scored.append((score, section))

    scored.sort(key=lambda x: -x[0])
    top = scored[:4]  # Top 4 most relevant sections

    if not top:
        # Fallback: return the summary section at end of file
        for section in reversed(sections):
            if "What this all means" in section or "Summary" in section.lower():
                return section[:1200]
        return full_text[-800:]  # last 800 chars as final fallback

    result = "\n\n".join(s for _, s in top)
    return result[:2500]  # cap at 2500 chars to not bloat the prompt


def get_macro_context(pair: str) -> str:
    """Return relevant macro context for a pair from datamacro.md."""
    text = _load_macro_md()
    if not text:
        logger.warning("datamacro.md not found or empty")
        return ""
    extracted = _extract_macro_for_pair(pair, text)
    if extracted:
        logger.info(f"Loaded macro context for {pair}: {len(extracted)} chars")
    return extracted


def build_ohlcv_from_ticks(
    ticks: List[Dict],
    timeframe_minutes: int,
    max_candles: int = 50,
) -> List[Dict]:
    """Aggregate tick data into OHLCV candles."""
    if not ticks:
        return []

    interval = timeframe_minutes * 60
    candles: Dict[int, Dict] = {}

    for tick in ticks:
        try:
            t = int(tick.get("time", 0))
            mid = (float(tick.get("bid", 0)) + float(tick.get("ask", 0))) / 2
            if mid <= 0:
                continue
            bucket = (t // interval) * interval
            if bucket not in candles:
                candles[bucket] = {
                    "time": bucket,
                    "open": mid, "high": mid, "low": mid, "close": mid,
                    "volume": 0,
                }
            else:
                c = candles[bucket]
                c["high"] = max(c["high"], mid)
                c["low"]  = min(c["low"],  mid)
                c["close"] = mid
                c["volume"] += int(tick.get("volume", 1))
        except Exception:
            continue

    sorted_candles = sorted(candles.values(), key=lambda x: x["time"])
    return sorted_candles[-max_candles:]


def format_candles_for_prompt(candles: List[Dict], tf_label: str, pair: str) -> str:
    """Format candle list into a compact human-readable string for the AI prompt."""
    if not candles:
        return f"{tf_label}: No data available"

    lines = [f"{tf_label} ({len(candles)} candles, {pair}):"]
    # Show last 10 candles in compact format
    for c in candles[-10:]:
        dt = datetime.fromtimestamp(c["time"], tz=timezone.utc).strftime("%m-%d %H:%M")
        lines.append(
            f"  {dt}  O={c['open']:.3f}  H={c['high']:.3f}"
            f"  L={c['low']:.3f}  C={c['close']:.3f}  V={c['volume']}"
        )

    # Add simple stats
    if len(candles) >= 2:
        first_open = candles[0]["open"]
        last_close = candles[-1]["close"]
        highs = [c["high"] for c in candles]
        lows  = [c["low"]  for c in candles]
        pct = (last_close - first_open) / first_open * 100
        lines.append(
            f"  Range: {min(lows):.3f}–{max(highs):.3f} | "
            f"Net: {'+' if pct>=0 else ''}{pct:.2f}% | "
            f"Current: {last_close:.3f}"
        )
    return "\n".join(lines)


class RedisMarketData:
    """Reads live tick data from Redis and builds OHLCV candles."""

    def __init__(self):
        self._redis = None

    def _get_redis(self):
        if self._redis is None:
            try:
                import redis as redis_lib
                self._redis = redis_lib.from_url(settings.redis_url, decode_responses=True)
                self._redis.ping()
                logger.info("RedisMarketData connected to Redis")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}")
                self._redis = None
        return self._redis

    def get_ticks(self, pair: str, count: int = 1000) -> List[Dict]:
        """Fetch raw ticks for a pair from Redis."""
        r = self._get_redis()
        if not r:
            return []
        try:
            key = f"ticks:{pair}"
            raw = r.lrange(key, 0, count - 1)
            return [json.loads(x) for x in raw]
        except Exception as e:
            logger.warning(f"Failed to fetch ticks for {pair}: {e}")
            return []

    def get_latest_price(self, pair: str) -> Optional[float]:
        """Get latest mid price for a pair."""
        ticks = self.get_ticks(pair, 1)
        if not ticks:
            return None
        t = ticks[0]
        bid = float(t.get("bid", 0))
        ask = float(t.get("ask", 0))
        return (bid + ask) / 2 if bid and ask else None

    async def _fetch_ohlcv_from_service(self, symbol: str, timeframe: str, count: int) -> List[Dict]:
        """Fetch historical candles from gas-mt5-data-service."""
        import httpx
        url = f"{settings.mt5_data_service_url}/history"
        params = {
            "symbol": symbol,
            "timeframe": timeframe,
            "count": count
        }
        headers = {"X-User-ID": "system-ai-orchestrator"}
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", [])
                else:
                    logger.warning(f"Data service error: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Failed to fetch from data service: {e}")
        return []

    async def build_multi_tf_ohlcv(self, pair: str) -> str:
        """Build OHLCV string for multiple timeframes. 
        Uses gas-mt5-data-service for reliable historical data."""
        
        logger.info(f"Building multi-TF OHLCV for {pair} using Data Service")

        # Timeframes to fetch
        tf_configs = [
            ("H4",  "H4",  30),
            ("H1",  "H1",  50),
            ("M15", "M15", 80),
            ("M5",  "M5",  50),
        ]

        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        parts = [f"[HISTORICAL OHLCV — {pair} — {now} — source: gas-mt5-data-service]"]

        import asyncio
        tasks = [self._fetch_ohlcv_from_service(pair, tf_name, count) for _, tf_name, count in tf_configs]
        results = await asyncio.gather(*tasks)

        for i, (label, _, _) in enumerate(tf_configs):
            candles = results[i]
            parts.append(format_candles_for_prompt(candles, label, pair))

        # Add current "Live" price from ticks if available
        latest_price = self.get_latest_price(pair)
        if latest_price:
            parts.append(f"\n[LIVE TICK PRICE]: {latest_price:.5f}")

        return "\n\n".join(parts)


# Singleton
market_data = RedisMarketData()
