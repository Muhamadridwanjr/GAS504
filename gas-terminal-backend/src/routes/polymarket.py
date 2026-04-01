"""GAS Terminal Backend — Polymarket Service Proxy."""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from src.config import settings
from src.services.client import get_client

router = APIRouter(tags=["Polymarket"])


@router.get("/terminal/polymarket/health")
async def polymarket_health():
    client = await get_client()
    try:
        resp = await client.get(f"{settings.POLYMARKET_SERVICE_URL}/health")
        return resp.json()
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@router.get("/terminal/polymarket/markets")
async def polymarket_markets(
    category: str = Query("all"),
    limit: int = Query(30, le=100),
    search: Optional[str] = Query(None),
    active_only: bool = Query(True),
):
    client = await get_client()
    try:
        params = {"category": category, "limit": limit, "active_only": active_only}
        if search:
            params["search"] = search
        resp = await client.get(
            f"{settings.POLYMARKET_SERVICE_URL}/polymarket/markets",
            params=params,
            timeout=20.0,
        )
        if resp.status_code == 200:
            return resp.json()
        raise HTTPException(status_code=resp.status_code, detail="Polymarket service error")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/terminal/polymarket/predict")
async def polymarket_predict(body: dict):
    client = await get_client()
    try:
        resp = await client.post(
            f"{settings.POLYMARKET_SERVICE_URL}/polymarket/predict",
            json=body,
            timeout=30.0,
        )
        if resp.status_code == 200:
            return resp.json()
        raise HTTPException(status_code=resp.status_code, detail="Prediction failed")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/terminal/polymarket/history")
async def polymarket_history(limit: int = Query(20, le=100)):
    client = await get_client()
    try:
        resp = await client.get(
            f"{settings.POLYMARKET_SERVICE_URL}/polymarket/history",
            params={"limit": limit},
            timeout=10.0,
        )
        if resp.status_code == 200:
            return resp.json()
        raise HTTPException(status_code=resp.status_code, detail="History fetch failed")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/terminal/polymarket/analytics")
async def polymarket_analytics():
    client = await get_client()
    try:
        resp = await client.get(
            f"{settings.POLYMARKET_SERVICE_URL}/polymarket/analytics",
            timeout=10.0,
        )
        if resp.status_code == 200:
            return resp.json()
        raise HTTPException(status_code=resp.status_code, detail="Analytics fetch failed")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/terminal/polymarket/categories")
async def polymarket_categories():
    client = await get_client()
    try:
        resp = await client.get(
            f"{settings.POLYMARKET_SERVICE_URL}/polymarket/categories",
            timeout=10.0,
        )
        if resp.status_code == 200:
            return resp.json()
        raise HTTPException(status_code=resp.status_code, detail="Categories fetch failed")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/terminal/polymarket/top5")
async def polymarket_top5():
    client = await get_client()
    try:
        resp = await client.get(
            f"{settings.POLYMARKET_SERVICE_URL}/polymarket/top5",
            timeout=15.0,
        )
        if resp.status_code == 200:
            return resp.json()
        raise HTTPException(status_code=resp.status_code, detail="Top5 fetch failed")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/terminal/polymarket/agents/info")
async def polymarket_agents_info():
    client = await get_client()
    try:
        resp = await client.get(
            f"{settings.POLYMARKET_SERVICE_URL}/polymarket/agents/info",
            timeout=10.0,
        )
        if resp.status_code == 200:
            return resp.json()
        raise HTTPException(status_code=resp.status_code, detail="Agents info fetch failed")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
