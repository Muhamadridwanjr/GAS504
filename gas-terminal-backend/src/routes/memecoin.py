"""GAS Terminal Backend — Memecoin Service Proxy."""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from src.config import settings
from src.services.client import get_client

router = APIRouter(tags=["Memecoin"])

@router.get("/terminal/memecoin/health")
async def memecoin_health():
    client = await get_client()
    try:
        resp = await client.get(f"{settings.MEMECOIN_SERVICE_URL}/health")
        return resp.json()
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@router.get("/terminal/memecoin/chains")
async def memecoin_chains():
    client = await get_client()
    try:
        resp = await client.get(f"{settings.MEMECOIN_SERVICE_URL}/memecoin/chains", timeout=8.0)
        if resp.status_code == 200: return resp.json()
        raise HTTPException(status_code=resp.status_code, detail="Chains fetch failed")
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=503, detail=str(e))

@router.get("/terminal/memecoin/trending")
async def memecoin_trending(
    chain: str = Query("all"),
    limit: int = Query(30, le=60),
    min_liquidity: float = Query(10000),
    min_age: float = Query(10),
    max_age: float = Query(1440),
):
    client = await get_client()
    try:
        resp = await client.get(
            f"{settings.MEMECOIN_SERVICE_URL}/memecoin/trending",
            params={"chain": chain, "limit": limit, "min_liquidity": min_liquidity,
                    "min_age": min_age, "max_age": max_age},
            timeout=25.0,
        )
        if resp.status_code == 200: return resp.json()
        raise HTTPException(status_code=resp.status_code, detail="Trending fetch failed")
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=503, detail=str(e))

@router.get("/terminal/memecoin/search")
async def memecoin_search(q: str = Query(...), limit: int = Query(15, le=30)):
    client = await get_client()
    try:
        resp = await client.get(
            f"{settings.MEMECOIN_SERVICE_URL}/memecoin/search",
            params={"q": q, "limit": limit},
            timeout=15.0,
        )
        if resp.status_code == 200: return resp.json()
        raise HTTPException(status_code=resp.status_code, detail="Search failed")
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=503, detail=str(e))

@router.get("/terminal/memecoin/history")
async def memecoin_history(limit: int = Query(20, le=100)):
    client = await get_client()
    try:
        resp = await client.get(f"{settings.MEMECOIN_SERVICE_URL}/memecoin/history", params={"limit": limit}, timeout=10.0)
        if resp.status_code == 200: return resp.json()
        raise HTTPException(status_code=resp.status_code, detail="History fetch failed")
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=503, detail=str(e))

@router.get("/terminal/memecoin/stats")
async def memecoin_stats():
    client = await get_client()
    try:
        resp = await client.get(f"{settings.MEMECOIN_SERVICE_URL}/memecoin/stats", timeout=10.0)
        if resp.status_code == 200: return resp.json()
        raise HTTPException(status_code=resp.status_code, detail="Stats fetch failed")
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=503, detail=str(e))
