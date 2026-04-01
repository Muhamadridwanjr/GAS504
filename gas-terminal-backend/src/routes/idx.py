"""
IDX (Indonesia Stock Exchange) proxy route.
Forwards requests to gas-idx-service:9615
"""
import os
import httpx
from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/terminal/idx", tags=["IDX"])

IDX_SERVICE_URL = os.getenv("IDX_SERVICE_URL", "http://gas-idx-service:9615")
TIMEOUT = 20.0


async def _proxy(path: str, params: dict = None) -> dict:
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.get(f"{IDX_SERVICE_URL}/idx{path}", params=params or {})
        resp.raise_for_status()
        return resp.json()


@router.get("/health")
async def health():
    try:
        return await _proxy("/health")
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@router.get("/ihsg")
async def ihsg():
    return await _proxy("/ihsg")


@router.get("/quote")
async def quote(symbol: str = Query(...)):
    return await _proxy("/quote", {"symbol": symbol})


@router.get("/tickers")
async def tickers(symbols: str = Query(None)):
    params = {"symbols": symbols} if symbols else {}
    return await _proxy("/tickers", params)


@router.get("/ohlcv")
async def ohlcv(
    symbol: str = Query(...),
    interval: str = Query("1d"),
    period: str = Query("3mo"),
):
    return await _proxy("/ohlcv", {"symbol": symbol, "interval": interval, "period": period})


@router.get("/analysis")
async def analysis(
    symbol: str = Query(...),
    interval: str = Query("1d"),
    period: str = Query("6mo"),
):
    return await _proxy("/analysis", {"symbol": symbol, "interval": interval, "period": period})


@router.get("/signal")
async def signal(
    symbol: str = Query(...),
    interval: str = Query("1d"),
    period: str = Query("6mo"),
):
    return await _proxy("/signal", {"symbol": symbol, "interval": interval, "period": period})


@router.get("/smc")
async def smc(
    symbol: str = Query(...),
    interval: str = Query("1d"),
    style: str = Query("swing"),
):
    return await _proxy("/smc", {"symbol": symbol, "interval": interval, "style": style})


@router.get("/top_gainer")
async def top_gainer(n: int = Query(10)):
    return await _proxy("/top_gainer", {"n": n})


@router.get("/top_loser")
async def top_loser(n: int = Query(10)):
    return await _proxy("/top_loser", {"n": n})


@router.get("/most_active")
async def most_active(n: int = Query(10)):
    return await _proxy("/most_active", {"n": n})


@router.get("/companies")
async def companies():
    return await _proxy("/companies")
