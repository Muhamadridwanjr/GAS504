"""GAS Memecoin Service — API Routes."""
import json
import logging
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
import redis.asyncio as aioredis

from ..config import settings
from ..core.dexscreener import fetch_trending_tokens, fetch_token_by_address, search_tokens, SUPPORTED_CHAINS
from ..core.rug_detector import detect_rug
from ..core.scoring import score_token
from ..core.ai_engine import run_ai_analysis, build_ai_consensus

logger = logging.getLogger("memecoin_routes")
router = APIRouter(prefix="/memecoin", tags=["Memecoin"])

_redis: Optional[aioredis.Redis] = None

async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = await aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


@router.get("/health")
async def health():
    return {"status": "ok", "service": "gas-memecoin-service"}


@router.get("/chains")
async def get_chains():
    return {
        "chains": [
            {"id": "all",      "label": "All Chains",  "color": "#6366f1"},
            {"id": "solana",   "label": "Solana",       "color": "#9945ff"},
            {"id": "ethereum", "label": "Ethereum",     "color": "#627eea"},
            {"id": "base",     "label": "Base",         "color": "#0052ff"},
            {"id": "bsc",      "label": "BSC",          "color": "#f0b90b"},
            {"id": "arbitrum", "label": "Arbitrum",     "color": "#28a0f0"},
        ]
    }


@router.get("/trending")
async def get_trending(
    chain: str = Query("all"),
    limit: int = Query(30, le=60),
    min_liquidity: float = Query(10000),
    min_age: float = Query(10),
    max_age: float = Query(1440),
):
    """Fetch trending tokens with basic rug scores (no AI, fast)."""
    redis = await get_redis()
    cache_key = f"gas:meme:trending:{chain}:{limit}:{int(min_liquidity)}"

    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    tokens = await fetch_trending_tokens(
        chain=None if chain == "all" else chain,
        limit=limit,
        min_liquidity=min_liquidity,
        min_age=min_age,
        max_age=max_age,
    )

    # Quick rug + score for each token (no AI)
    enriched = []
    for t in tokens:
        rug = detect_rug(t)
        score, signal, risk = score_token(t, rug)
        enriched.append({
            **t,
            "rug": rug,
            "score": score,
            "signal": signal,
            "risk": risk,
        })

    # Sort: BUY EARLY first, then DANGER last
    signal_order = {"BUY EARLY": 0, "BUY MOMENTUM": 1, "WEAK TREND": 2, "AVOID": 3, "EXIT NOW": 4, "DANGER": 5}
    enriched.sort(key=lambda x: (signal_order.get(x["signal"], 3), -x["score"]))

    result = {
        "tokens": enriched,
        "total": len(enriched),
        "chain": chain,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    await redis.setex(cache_key, settings.CACHE_TTL, json.dumps(result))
    return result


@router.post("/signal")
async def get_signal(body: dict):
    """
    Full AI analysis for a specific token.
    Body: {token_address: str, chain: str} OR full token dict.
    Returns: complete signal with 4 AI agents + consensus.
    """
    token_address = body.get("token_address", "")
    chain = body.get("chain", "")

    redis = await get_redis()
    cache_key = f"gas:meme:signal:{token_address}"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    # Fetch token data if not provided in body
    if "symbol" in body and "price_usd" in body:
        token = {k: v for k, v in body.items() if k not in ("token_address",)}
        token["token_address"] = token_address
    else:
        token = await fetch_token_by_address(token_address)
        if not token:
            raise HTTPException(status_code=404, detail=f"Token {token_address} not found on Dexscreener")

    # Rug detection
    rug = detect_rug(token)

    # Composite score
    score, signal, risk = score_token(token, rug)

    # AI analysis (4 models)
    agents = await run_ai_analysis(token, rug)
    consensus = build_ai_consensus(agents)

    # Final signal: blend composite + AI consensus
    final_signal = consensus["signal"] if consensus["confidence"] > 0.6 else signal

    result = {
        "token_address": token_address,
        "symbol":        token.get("symbol", "UNKNOWN"),
        "name":          token.get("name", ""),
        "chain":         token.get("chain", chain),
        "signal":        final_signal,
        "score":         score,
        "risk":          risk,
        "rug":           rug,
        "agents":        agents,
        "consensus_signal":     consensus["signal"],
        "consensus_confidence": consensus["confidence"],
        "consensus_score":      consensus["score"],
        "price_usd":     token.get("price_usd", 0),
        "liquidity_usd": token.get("liquidity_usd", 0),
        "volume_1h":     token.get("volume_1h", 0),
        "buy_pressure":  token.get("buy_pressure", 0.5),
        "price_change_1h": token.get("price_change_1h", 0),
        "price_change_5m": token.get("price_change_5m", 0),
        "buys_1h":       token.get("buys_1h", 0),
        "sells_1h":      token.get("sells_1h", 0),
        "age_minutes":   token.get("age_minutes", 0),
        "dex_url":       token.get("dex_url", ""),
        "dex_id":        token.get("dex_id", ""),
        "timestamp":     datetime.now(timezone.utc).isoformat(),
    }

    await redis.setex(cache_key, settings.SIGNAL_CACHE_TTL, json.dumps(result))

    # Store in signal history
    await redis.lpush("gas:meme:history", json.dumps({
        "symbol":  result["symbol"],
        "chain":   result["chain"],
        "signal":  result["signal"],
        "score":   result["score"],
        "risk":    result["risk"],
        "ts":      result["timestamp"],
    }))
    await redis.ltrim("gas:meme:history", 0, 299)

    return result


@router.get("/search")
async def search(q: str = Query(..., min_length=2), limit: int = Query(15, le=30)):
    """Search tokens by symbol or name."""
    redis = await get_redis()
    cache_key = f"gas:meme:search:{q.lower()}:{limit}"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    tokens = await search_tokens(q, limit)
    enriched = []
    for t in tokens:
        rug = detect_rug(t)
        score, signal, risk = score_token(t, rug)
        enriched.append({**t, "rug": rug, "score": score, "signal": signal, "risk": risk})

    result = {"tokens": enriched, "total": len(enriched), "query": q}
    await redis.setex(cache_key, 60, json.dumps(result))
    return result


@router.get("/history")
async def get_history(limit: int = Query(20, le=100)):
    redis = await get_redis()
    raw = await redis.lrange("gas:meme:history", 0, limit - 1)
    return {"history": [json.loads(r) for r in raw], "total": len(raw)}


@router.get("/stats")
async def get_stats():
    redis = await get_redis()
    raw = await redis.lrange("gas:meme:history", 0, 299)
    history = [json.loads(r) for r in raw]
    if not history:
        return {"total_signals": 0, "by_signal": {}, "by_chain": {}, "by_risk": {}}
    by_sig   = {}
    by_chain = {}
    by_risk  = {}
    for h in history:
        s = h.get("signal","AVOID");  by_sig[s]   = by_sig.get(s, 0) + 1
        c = h.get("chain","unknown"); by_chain[c] = by_chain.get(c, 0) + 1
        r = h.get("risk","HIGH");     by_risk[r]  = by_risk.get(r, 0) + 1
    return {"total_signals": len(history), "by_signal": by_sig, "by_chain": by_chain, "by_risk": by_risk}
