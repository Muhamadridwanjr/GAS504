"""GAS Polymarket Service — API Routes."""
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
import redis.asyncio as aioredis

from ..config import settings
from ..core.gamma_client import fetch_markets, generate_gas_events
from ..core.prediction_engine import predict_single
from ..core.consensus_engine import run_agent_predictions, build_consensus, AGENT_SPEC
from ..models.schemas import PredictRequest

logger = logging.getLogger("polymarket_routes")
router = APIRouter(prefix="/polymarket", tags=["Polymarket"])

_redis: Optional[aioredis.Redis] = None

async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = await aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


@router.get("/health")
async def health():
    return {"status": "ok", "service": "gas-polymarket-service"}


@router.get("/markets")
async def get_markets(
    category: Optional[str] = Query("all"),
    limit: int = Query(40, le=100),
    search: Optional[str] = Query(None),
    active_only: bool = Query(True),
):
    """Fetch filtered Polymarket events + GAS-generated events."""
    redis = await get_redis()
    cache_key = f"gas:poly:markets2:{category}:{limit}:{search}"

    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    markets = await fetch_markets(
        limit=limit,
        category=None if category == "all" else category,
        active_only=active_only,
        search=search,
    )

    result = {
        "markets": markets,
        "total": len(markets),
        "category": category,
        "sources": {
            "polymarket": sum(1 for m in markets if m.get("source") == "polymarket"),
            "gas_generated": sum(1 for m in markets if m.get("source") == "gas"),
        }
    }
    await redis.setex(cache_key, settings.CACHE_TTL, json.dumps(result))
    return result


@router.post("/predict")
async def predict_market(body: PredictRequest):
    """Run multi-agent weighted prediction on a market event."""
    redis = await get_redis()
    cache_key = f"gas:poly:predict2:{body.event_id}"

    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    # Run all model predictions concurrently
    agents = await run_agent_predictions(
        question=body.question,
        category=body.category,
        yes_price=body.yes_price,
        no_price=body.no_price,
        pair=body.pair,
        selected_models=body.models,
    )

    consensus = build_consensus(agents)

    # Single-model signal (Claude as primary)
    signal = await predict_single(
        question=body.question,
        category=body.category,
        yes_price=body.yes_price,
        no_price=body.no_price,
        pair=body.pair,
        model="claude",
    )

    result = {
        "event_id": body.event_id,
        "question": body.question,
        "category": body.category,
        "signal": signal,
        "agents": agents,
        "consensus": consensus,
        "pair": body.pair,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    await redis.setex(cache_key, settings.PREDICT_CACHE_TTL, json.dumps(result))

    # Store in history
    await redis.lpush("gas:poly:history", json.dumps({
        "event_id": body.event_id,
        "question": body.question,
        "category": body.category,
        "action": consensus["action"],
        "signal_strength": consensus.get("signal_strength", consensus["action"]),
        "confidence": consensus["confidence"],
        "yes": consensus["yes"],
        "pair": body.pair,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }))
    await redis.ltrim("gas:poly:history", 0, 499)

    return result


@router.get("/top5")
async def get_top5():
    """
    Return today's top 5 high-confidence trading predictions.
    Picks from GAS-generated events sorted by confidence distance from 50%.
    """
    redis = await get_redis()
    cache_key = f"gas:poly:top5:{datetime.now(timezone.utc).strftime('%Y%m%d%H')}"

    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    # Get candidate events (GAS-generated, all pairs)
    candidates = generate_gas_events(max_per_pair=3)

    # Score each by how far yes_price is from 50% (more decisive = higher rank)
    scored = []
    for c in candidates:
        score = abs(c["yes_price"] - 0.5)  # 0..0.5, higher = more decisive
        scored.append({**c, "_score": score})

    # Sort by score desc, take top 5
    top5 = sorted(scored, key=lambda x: x["_score"], reverse=True)[:5]
    for e in top5:
        e.pop("_score", None)

    result = {"picks": top5, "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "count": len(top5)}
    await redis.setex(cache_key, 3600, json.dumps(result))  # 1h cache
    return result


@router.get("/history")
async def get_history(limit: int = Query(20, le=100)):
    redis = await get_redis()
    raw = await redis.lrange("gas:poly:history", 0, limit - 1)
    history = [json.loads(r) for r in raw]
    return {"history": history, "total": len(history)}


@router.get("/analytics")
async def get_analytics():
    redis = await get_redis()
    raw = await redis.lrange("gas:poly:history", 0, 499)
    history = [json.loads(r) for r in raw]

    total = len(history)
    if total == 0:
        return {
            "total_predictions": 0, "by_category": {}, "by_action": {},
            "by_signal_strength": {}, "recent_confidence_avg": 0,
        }

    by_cat: dict = {}
    by_action: dict = {}
    by_strength: dict = {}
    conf_sum = 0.0

    for h in history:
        cat = h.get("category", "general")
        by_cat[cat] = by_cat.get(cat, 0) + 1
        act = h.get("action", "NO TRADE")
        by_action[act] = by_action.get(act, 0) + 1
        strength = h.get("signal_strength", act)
        by_strength[strength] = by_strength.get(strength, 0) + 1
        conf_sum += float(h.get("confidence", 0))

    return {
        "total_predictions": total,
        "by_category": by_cat,
        "by_action": by_action,
        "by_signal_strength": by_strength,
        "recent_confidence_avg": round(conf_sum / total, 1),
    }


@router.get("/agents/info")
async def get_agents_info():
    """Return agent specialization metadata."""
    return {
        "agents": [
            {
                "model": model,
                "specialty": spec["specialty"],
                "weight": spec["weight"],
                "color": spec["color"],
            }
            for model, spec in AGENT_SPEC.items()
        ]
    }


@router.get("/categories")
async def get_categories():
    return {
        "categories": [
            {"id": "all",       "label": "All Markets",    "color": "#6366f1"},
            {"id": "crypto",    "label": "Crypto",          "color": "#f59e0b"},
            {"id": "forex",     "label": "Forex & Gold",    "color": "#10b981"},
            {"id": "macro",     "label": "Macro",           "color": "#3b82f6"},
            {"id": "intraday",  "label": "Intraday",        "color": "#f43f5e"},
            {"id": "technical", "label": "Technical / SMC", "color": "#8b5cf6"},
        ]
    }
