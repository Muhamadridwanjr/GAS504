from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
import httpx
import os
import time

from ..core.fetcher import (
    get_quote, get_ohlcv, get_multi_quote, get_ihsg,
    get_company_info, IDX_SYMBOLS
)
from ..core.indicators import full_analysis
from ..core.scanner import get_top_gainer, get_top_loser, get_most_active

router = APIRouter(prefix="/idx", tags=["IDX"])

SMC_ENGINE_URL = os.getenv("SMC_ENGINE_URL", "http://gas-smc-engine:8000")

# ── Market Overview ─────────────────────────────────────────────
@router.get("/health")
def health():
    return {"status": "ok", "service": "gas-idx-service", "version": "1.0.0"}

@router.get("/ihsg")
def ihsg():
    return get_ihsg()

@router.get("/quote")
def quote(symbol: str = Query(..., description="IDX symbol, e.g. BBCA")):
    return get_quote(symbol)

@router.get("/tickers")
def tickers(symbols: str = Query(None, description="Comma-separated symbols, default: top 20")):
    syms = [s.strip().upper() for s in symbols.split(",")] if symbols else IDX_SYMBOLS[:20]
    return {"symbols": get_multi_quote(syms), "count": len(syms), "timestamp": int(time.time())}

@router.get("/ohlcv")
def ohlcv(
    symbol: str = Query(...),
    interval: str = Query("1d", description="1m/5m/15m/30m/1h/1d/1wk"),
    period: str = Query("3mo", description="1d/5d/1mo/3mo/6mo/1y/2y/5y"),
):
    valid_intervals = ["1m","2m","5m","15m","30m","60m","1h","1d","1wk","1mo"]
    if interval not in valid_intervals:
        raise HTTPException(400, f"Invalid interval. Use: {valid_intervals}")
    candles = get_ohlcv(symbol, interval, period)
    return {"symbol": symbol.upper(), "interval": interval, "period": period, "candles": candles, "count": len(candles)}

# ── Technical Analysis ──────────────────────────────────────────
@router.get("/analysis")
def analysis(
    symbol: str = Query(...),
    interval: str = Query("1d"),
    period: str = Query("6mo"),
):
    candles = get_ohlcv(symbol, interval, period)
    if not candles or len(candles) < 20:
        raise HTTPException(400, f"Insufficient data for {symbol}. Got {len(candles)} candles.")
    result = full_analysis(candles)
    result["symbol"] = symbol.upper()
    result["interval"] = interval
    return result

# ── SMC Analysis ────────────────────────────────────────────────
@router.get("/smc")
async def smc_analysis(
    symbol: str = Query(...),
    interval: str = Query("1d"),
    period: str = Query("6mo"),
    style: str = Query("swing", description="scalping/intraday/swing"),
):
    candles = get_ohlcv(symbol, interval, period)
    if not candles or len(candles) < 20:
        raise HTTPException(400, "Insufficient data for SMC analysis.")
    timeframe_map = {"1m":"M1","5m":"M5","15m":"M15","30m":"M30","1h":"H1","1d":"D1","1wk":"W1"}
    tf = timeframe_map.get(interval, "D1")
    payload = {
        "symbol": symbol.upper(),
        "timeframe": tf,
        "candles": candles[-200:],
        "options": {
            "trading_style": style,
            "include_filters": ["kill_zones", "amd"],
            "detect": ["market_structure", "zones", "liquidity", "entry"],
        }
    }
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(f"{SMC_ENGINE_URL}/detect", json=payload)
            smc_result = resp.json()
    except Exception as e:
        smc_result = {"error": str(e), "note": "SMC engine unavailable"}
    return {"symbol": symbol.upper(), "interval": interval, "smc": smc_result}

# ── Full AI Signal (Indicators + SMC combined) ──────────────────
@router.get("/signal")
async def full_signal(
    symbol: str = Query(...),
    interval: str = Query("1d"),
    period: str = Query("6mo"),
):
    candles = get_ohlcv(symbol, interval, period)
    if not candles or len(candles) < 20:
        raise HTTPException(400, "Insufficient candle data.")

    # Run indicators
    tech = full_analysis(candles)

    # Run SMC
    timeframe_map = {"1m":"M1","5m":"M5","15m":"M15","1h":"H1","1d":"D1","1wk":"W1"}
    tf = timeframe_map.get(interval, "D1")
    smc_result = {}
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(f"{SMC_ENGINE_URL}/detect", json={
                "symbol": symbol.upper(),
                "timeframe": tf,
                "candles": candles[-200:],
                "options": {"trading_style": "swing", "include_filters": [], "detect": ["market_structure","zones","liquidity","entry"]}
            })
            smc_result = resp.json()
    except:
        smc_result = {}

    # Company info
    info = get_company_info(symbol)

    # Combine scores
    tech_score = tech.get("signal", {}).get("score", 50)
    smc_score = smc_result.get("confluence_score", 50) if smc_result and "confluence_score" in smc_result else tech_score
    final_score = round((tech_score * 0.6 + smc_score * 0.4), 1)

    if final_score >= 68:
        action, color = "BUY", "green"
    elif final_score <= 32:
        action, color = "SELL", "red"
    else:
        action, color = "HOLD", "yellow"

    return {
        "symbol": symbol.upper(),
        "interval": interval,
        "company": info,
        "quote": get_quote(symbol),
        "technical": tech,
        "smc": smc_result,
        "final_signal": {
            "action": action,
            "score": final_score,
            "tech_score": tech_score,
            "smc_score": smc_score,
            "color": color,
        }
    }

# ── Scanner ─────────────────────────────────────────────────────
@router.get("/top_gainer")
def top_gainer(n: int = Query(10, le=20)):
    return {"data": get_top_gainer(n), "timestamp": int(time.time())}

@router.get("/top_loser")
def top_loser(n: int = Query(10, le=20)):
    return {"data": get_top_loser(n), "timestamp": int(time.time())}

@router.get("/most_active")
def most_active(n: int = Query(10, le=20)):
    return {"data": get_most_active(n), "timestamp": int(time.time())}

@router.get("/companies")
def companies():
    return {"symbols": IDX_SYMBOLS, "count": len(IDX_SYMBOLS)}
