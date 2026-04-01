"""
SMC Fetcher — Calls gas-smc-engine with OHLCV data.
Handles both Binance (crypto) and MT5 Redis (forex/commodity) as data source.
"""
import httpx
import os
import logging
from typing import List, Dict, Any, Optional

from src.data.redis_mt5 import get_ohlc_smart

log = logging.getLogger("gas.smc_fetcher")

SMC_ENGINE_URL = os.getenv("SMC_ENGINE_URL", "http://gas-smc-engine:8006")

# Trading style → primary timeframe for SMC analysis
STYLE_TF_MAP = {
    "scalping": "M15",
    "intraday": "H1",
    "swing":    "H4",
}


async def run_smc_analysis(
    symbol: str,
    timeframe: str = "H1",
    trading_style: str = "intraday",
    limit: int = 200,
) -> Optional[Dict[str, Any]]:
    """
    Fetch OHLCV data (auto-routed: Binance for crypto, MT5 Redis for forex),
    then POST to gas-smc-engine /detect and return SMC analysis.
    Returns None if data unavailable or engine fails.
    """
    # 1. Fetch candles via smart router (Binance or MT5)
    candles = await get_ohlc_smart(symbol, timeframe, limit=limit)
    if not candles or len(candles) < 20:
        log.warning(f"SMC: insufficient candles for {symbol}/{timeframe} ({len(candles) if candles else 0} bars)")
        return None

    # 2. Build request payload for gas-smc-engine
    payload = {
        "symbol":    symbol,
        "timeframe": timeframe,
        "candles":   candles,
        "options":   {
            "trading_style":   trading_style,
            "include_filters": ["kill_zones", "amd"],
            "detect":          ["market_structure", "zones", "liquidity", "entry"],
        },
    }

    # 3. Call gas-smc-engine
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(f"{SMC_ENGINE_URL}/detect", json=payload)
            resp.raise_for_status()
            result = resp.json()
            log.info(f"SMC analysis done: {symbol}/{timeframe} — score={result.get('confluence_score')} action={result.get('signal', {}).get('action')}")
            return result
    except httpx.HTTPStatusError as e:
        log.error(f"SMC engine HTTP error for {symbol}/{timeframe}: {e.response.status_code} {e.response.text[:200]}")
        return None
    except Exception as e:
        log.error(f"SMC engine call failed for {symbol}/{timeframe}: {e}")
        return None


async def run_smc_scanner(
    pairs: List[str],
    timeframe: str = "H4",
    trading_style: str = "swing",
    min_confluence: int = 60,
) -> List[Dict[str, Any]]:
    """
    Run SMC analysis on multiple pairs in parallel and return ranked results.
    Supports all Binance pairs + all MT5 forex/commodity pairs.
    """
    import asyncio

    async def _scan(symbol: str) -> Optional[Dict]:
        try:
            result = await run_smc_analysis(symbol, timeframe, trading_style)
            if not result:
                return None
            score  = result.get("confluence_score", 0)
            action = result.get("signal", {}).get("action", "WAIT")
            if score >= min_confluence and action in ("BUY", "SELL"):
                return {
                    "pair":            symbol,
                    "timeframe":       timeframe,
                    "confluence_score": score,
                    "signal":          action,
                    "bias":            result.get("market_structure", {}).get("bias", "NEUTRAL"),
                    "trade_quality":   result.get("signal", {}).get("trade_quality", "C"),
                    "amd_phase":       result.get("signal", {}).get("amd_phase", "UNKNOWN"),
                    "in_kill_zone":    result.get("signal", {}).get("in_kill_zone", False),
                    "bos":             bool(result.get("market_structure", {}).get("bos")),
                    "ob_count":        len(result.get("zones", {}).get("order_blocks", [])),
                    "fvg_count":       len(result.get("zones", {}).get("fvgs", [])),
                    "sweep":           bool(result.get("liquidity", {}).get("sweeps")),
                    "entry_price":     result.get("signal", {}).get("entry_price"),
                    "sl":              result.get("signal", {}).get("stop_loss"),
                    "tp":              result.get("signal", {}).get("take_profit"),
                    "rr":              result.get("signal", {}).get("rr"),
                    "reason":          result.get("signal", {}).get("reason", ""),
                }
        except Exception as e:
            log.warning(f"SMC scan failed for {symbol}: {e}")
        return None

    tasks = [_scan(p) for p in pairs]
    raw   = await asyncio.gather(*tasks)
    results = [r for r in raw if r is not None]
    results.sort(key=lambda x: x["confluence_score"], reverse=True)
    for i, r in enumerate(results):
        r["rank"] = i + 1
    return results
