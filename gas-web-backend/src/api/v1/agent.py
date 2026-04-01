"""
GAS AI Agent Trading System — Backend API
Stores agent configs & trade history in Redis.
Runs agent signals via strategy-core.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import httpx, json, uuid, os
from datetime import datetime, timezone
import redis.asyncio as aioredis

from ...core.dependencies import get_current_user_info

router = APIRouter(tags=["AI Agent System"])

REDIS_URL = os.getenv("REDIS_URL", "redis://gas-redis:6379/0")
STRATEGY_CORE_URL = os.getenv("STRATEGY_CORE_URL", "http://gas-strategy-core:7003")

_redis = None
async def _get_redis():
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis

def _agent_key(user_id: str) -> str:
    return f"gas:agent:{user_id}:agents"

def _history_key(user_id: str) -> str:
    return f"gas:agent:{user_id}:history"

# ── Models ────────────────────────────────────────────────────────────────────

class AgentCreate(BaseModel):
    name: str
    model_id: str  # claude | gpt | gemini | grok
    style: str     # scalping | intraday | swing
    pair: str      # XAUUSD, EURUSD, etc.
    min_confidence: int = 70
    max_trades: int = 2

class AgentRunRequest(BaseModel):
    agent_id: Optional[str] = None
    pair: str = "XAUUSD"
    style: str = "scalping"
    model: str = "claude"
    min_confidence: int = 70
    max_trades: int = 2
    timeframe: Optional[str] = None
    timeframes: Optional[List[str]] = None

class TradeRecord(BaseModel):
    agent_id: str
    signal: str
    entry: Optional[float] = None
    sl: Optional[float] = None
    tp: Optional[float] = None
    confidence: Optional[int] = None
    pair: str
    outcome: Optional[str] = None   # WIN | LOSS | OPEN
    pnl: Optional[float] = None

# ── Agent CRUD ────────────────────────────────────────────────────────────────

@router.get("/agent/agents")
async def get_agents(user_info: dict = Depends(get_current_user_info)):
    user_id = str(user_info.get("user_id", ""))
    r = await _get_redis()
    raw = await r.get(_agent_key(user_id))
    agents = json.loads(raw) if raw else []
    return {"agents": agents, "count": len(agents)}


@router.post("/agent/agents")
async def create_agent(data: AgentCreate, user_info: dict = Depends(get_current_user_info)):
    user_id = str(user_info.get("user_id", ""))
    r = await _get_redis()
    raw = await r.get(_agent_key(user_id))
    agents = json.loads(raw) if raw else []

    # Check plan — max agents per plan
    plan = user_info.get("plan", "essential")
    role = user_info.get("role", "user")
    max_slots = 999 if role == "admin" else {"essential": 1, "plus": 2, "premium": 3, "ultimate": 4, "ultra": 10}.get(plan, 1)
    active_count = sum(1 for a in agents if a.get("status") != "DISABLED")
    if active_count >= max_slots:
        raise HTTPException(status_code=403, detail=f"Plan {plan} hanya mendukung {max_slots} agent aktif. Upgrade plan atau disable agent lain.")

    agent = {
        "id": str(uuid.uuid4())[:8],
        "name": data.name,
        "model_id": data.model_id,
        "style": data.style,
        "pair": data.pair,
        "min_confidence": data.min_confidence,
        "max_trades": data.max_trades,
        "status": "ACTIVE",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "winrate": 0,
        "trades": 0,
        "wins": 0,
        "losses": 0,
        "pnl": 0.0,
        "last_signal": None,
        "confidence": None,
        "entry": None,
        "sl": None,
        "tp": None,
    }
    agents.append(agent)
    await r.set(_agent_key(user_id), json.dumps(agents))
    return {"status": "ok", "agent": agent}


@router.patch("/agent/agents/{agent_id}/toggle")
async def toggle_agent(agent_id: str, user_info: dict = Depends(get_current_user_info)):
    user_id = str(user_info.get("user_id", ""))
    r = await _get_redis()
    raw = await r.get(_agent_key(user_id))
    agents = json.loads(raw) if raw else []
    for ag in agents:
        if ag["id"] == agent_id:
            ag["status"] = "ACTIVE" if ag["status"] != "ACTIVE" else "COOLDOWN"
            break
    else:
        raise HTTPException(status_code=404, detail="Agent tidak ditemukan")
    await r.set(_agent_key(user_id), json.dumps(agents))
    return {"status": "ok", "agents": agents}


@router.delete("/agent/agents/{agent_id}")
async def delete_agent(agent_id: str, user_info: dict = Depends(get_current_user_info)):
    user_id = str(user_info.get("user_id", ""))
    r = await _get_redis()
    raw = await r.get(_agent_key(user_id))
    agents = json.loads(raw) if raw else []
    agents = [a for a in agents if a["id"] != agent_id]
    await r.set(_agent_key(user_id), json.dumps(agents))
    return {"status": "ok", "agents": agents}


# ── Agent Run ─────────────────────────────────────────────────────────────────

@router.post("/agent/run")
async def run_agent(data: AgentRunRequest, user_info: dict = Depends(get_current_user_info)):
    user_id = str(user_info.get("user_id", ""))
    role = user_info.get("role", "user")

    # Credit deduction (skip for admin)
    if role != "admin":
        r = await _get_redis()
        cr_key = f"gas:credits:{user_id}"
        credits_raw = await r.get(cr_key)
        credits = int(credits_raw or 0)
        cost = 5  # 5 credits per agent run
        if credits < cost:
            raise HTTPException(status_code=402, detail=f"Kredit tidak cukup. Butuh {cost}cr, tersedia {credits}cr.")
        await r.decrby(cr_key, cost)

    # Build request for strategy-core agent endpoint
    payload = {
        "pair": data.pair,
        "timeframe": data.timeframe or "M15",
        "model": data.model,
        "style": data.style,
        "min_confidence": data.min_confidence,
        "max_trades": data.max_trades,
        "user_id": user_id,
    }
    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            res = await client.post(f"{STRATEGY_CORE_URL}/v1/analysis/agent", json=payload)
            result = res.json() if res.status_code == 200 else {}
    except Exception as e:
        # Fallback: call technical endpoint and wrap as agent signal
        try:
            async with httpx.AsyncClient(timeout=40.0) as client:
                tech_res = await client.post(f"{STRATEGY_CORE_URL}/v1/analysis/technical", json={
                    "pair": data.pair, "timeframe": data.timeframe or "M15",
                    "indicators": ["RSI", "MACD", "ADX", "EMA50", "EMA200", "STOCH", "ATR"],
                    "user_id": user_id,
                })
                tech = tech_res.json() if tech_res.status_code == 200 else {}
                confidence = tech.get("confidence", 50)
                rec = tech.get("recommendation", "NEUTRAL")
                signal = rec if confidence >= data.min_confidence else "NO TRADE"
                result = {
                    "signal": signal,
                    "confidence": confidence,
                    "entry": tech.get("current_price"),
                    "sl": None,
                    "tp": None,
                    "reasoning": tech.get("ai_interpretation", "Analisa teknikal via fallback engine."),
                    "model_used": data.model,
                    "pair": data.pair,
                    "timeframe": data.timeframe or "M15",
                }
        except Exception as e2:
            result = {"signal": "NO TRADE", "confidence": 0, "reasoning": f"Gagal connect ke strategy-core: {e2}", "model_used": data.model, "pair": data.pair, "timeframe": data.timeframe or "M15"}

    # Update agent in Redis if agent_id provided
    if data.agent_id:
        r2 = await _get_redis()
        raw = await r2.get(_agent_key(user_id))
        agents = json.loads(raw) if raw else []
        for ag in agents:
            if ag["id"] == data.agent_id:
                ag["last_signal"] = result.get("signal")
                ag["confidence"] = result.get("confidence")
                ag["entry"] = result.get("entry")
                ag["sl"] = result.get("sl")
                ag["tp"] = result.get("tp", [None])[0] if isinstance(result.get("tp"), list) else result.get("tp")
                ag["trades"] = ag.get("trades", 0) + 1
                # Simple W/L tracking based on signal
                if result.get("signal") in ("BUY", "SELL"):
                    ag["wins"] = ag.get("wins", 0)  # will be updated on close
                break
        await r2.set(_agent_key(user_id), json.dumps(agents))

    # Store in history
    r3 = await _get_redis()
    hist_key = _history_key(user_id)
    raw_hist = await r3.get(hist_key)
    history = json.loads(raw_hist) if raw_hist else []
    history.insert(0, {
        "id": str(uuid.uuid4())[:8],
        "agent_id": data.agent_id or "solo",
        "agent_name": next((a["name"] for a in json.loads((await r3.get(_agent_key(user_id))) or "[]") if a["id"] == data.agent_id), "Solo Run") if data.agent_id else "Solo Run",
        "model": data.model,
        "pair": data.pair,
        "style": data.style,
        "signal": result.get("signal", "NO TRADE"),
        "confidence": result.get("confidence"),
        "entry": result.get("entry"),
        "sl": result.get("sl"),
        "tp": result.get("tp", [None])[0] if isinstance(result.get("tp"), list) else result.get("tp"),
        "outcome": "OPEN" if result.get("signal") in ("BUY", "SELL") else "NO_TRADE",
        "pnl": None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    if len(history) > 200:
        history = history[:200]
    await r3.set(hist_key, json.dumps(history))

    return result


# ── Performance & History ──────────────────────────────────────────────────────

@router.get("/agent/history")
async def get_history(limit: int = 50, user_info: dict = Depends(get_current_user_info)):
    user_id = str(user_info.get("user_id", ""))
    r = await _get_redis()
    raw = await r.get(_history_key(user_id))
    history = json.loads(raw) if raw else []
    return {"history": history[:limit], "total": len(history)}


@router.get("/agent/performance")
async def get_performance(user_info: dict = Depends(get_current_user_info)):
    user_id = str(user_info.get("user_id", ""))
    r = await _get_redis()

    # Load agents
    raw_ag = await r.get(_agent_key(user_id))
    agents = json.loads(raw_ag) if raw_ag else []

    # Load history
    raw_hist = await r.get(_history_key(user_id))
    history = json.loads(raw_hist) if raw_hist else []

    if not history:
        return {
            "agents": agents,
            "history": [],
            "stats": {
                "total_runs": 0,
                "total_signals": 0,
                "buy_signals": 0,
                "sell_signals": 0,
                "no_trade": 0,
                "avg_confidence": 0,
                "total_trades": sum(a.get("trades", 0) for a in agents),
                "total_pnl": sum(a.get("pnl", 0) for a in agents),
            },
            "model_stats": {},
            "pair_stats": {},
            "confidence_dist": {},
            "equity_curve": [],
            "daily_stats": {},
        }

    # Compute stats from history
    total = len(history)
    signals = [h for h in history if h.get("signal") in ("BUY", "SELL")]
    no_trades = [h for h in history if h.get("signal") == "NO TRADE"]
    confidences = [h["confidence"] for h in history if h.get("confidence") is not None]
    avg_conf = round(sum(confidences) / len(confidences), 1) if confidences else 0

    # Model breakdown
    model_stats = {}
    for h in history:
        m = h.get("model", "unknown")
        if m not in model_stats:
            model_stats[m] = {"runs": 0, "signals": 0, "avg_conf": 0, "conf_sum": 0}
        model_stats[m]["runs"] += 1
        if h.get("signal") in ("BUY", "SELL"):
            model_stats[m]["signals"] += 1
        if h.get("confidence"):
            model_stats[m]["conf_sum"] += h["confidence"]
    for m, s in model_stats.items():
        s["avg_conf"] = round(s["conf_sum"] / s["runs"], 1) if s["runs"] else 0

    # Pair breakdown
    pair_stats = {}
    for h in history:
        p = h.get("pair", "UNKNOWN")
        if p not in pair_stats:
            pair_stats[p] = {"runs": 0, "signals": 0}
        pair_stats[p]["runs"] += 1
        if h.get("signal") in ("BUY", "SELL"):
            pair_stats[p]["signals"] += 1

    # Confidence distribution buckets (50-55, 55-60, ..., 95-100)
    conf_dist = {}
    for h in history:
        c = h.get("confidence")
        if c is not None:
            bucket = f"{(c // 5) * 5}-{(c // 5) * 5 + 5}"
            conf_dist[bucket] = conf_dist.get(bucket, 0) + 1

    # Equity curve (cumulative PnL per run, using confidence as proxy)
    equity = []
    running = 0.0
    for h in reversed(history[:50]):
        if h.get("signal") in ("BUY", "SELL") and h.get("pnl") is not None:
            running += h["pnl"]
        elif h.get("signal") in ("BUY", "SELL"):
            c = h.get("confidence", 70)
            delta = (c - 65) * 0.5
            running += delta
        equity.append({"t": h.get("timestamp", "")[:10], "v": round(running, 2)})

    # Daily stats
    daily = {}
    for h in history:
        day = h.get("timestamp", "")[:10]
        if day:
            if day not in daily:
                daily[day] = {"runs": 0, "signals": 0}
            daily[day]["runs"] += 1
            if h.get("signal") in ("BUY", "SELL"):
                daily[day]["signals"] += 1

    return {
        "agents": agents,
        "history": history[:30],
        "stats": {
            "total_runs": total,
            "total_signals": len(signals),
            "buy_signals": sum(1 for h in history if h.get("signal") == "BUY"),
            "sell_signals": sum(1 for h in history if h.get("signal") == "SELL"),
            "no_trade": len(no_trades),
            "avg_confidence": avg_conf,
            "total_trades": sum(a.get("trades", 0) for a in agents),
            "total_pnl": round(sum(a.get("pnl", 0) for a in agents), 2),
        },
        "model_stats": model_stats,
        "pair_stats": pair_stats,
        "confidence_dist": conf_dist,
        "equity_curve": equity,
        "daily_stats": daily,
    }


@router.post("/agent/trade/close")
async def close_trade(record: TradeRecord, user_info: dict = Depends(get_current_user_info)):
    """Record trade outcome (WIN/LOSS) and update agent stats."""
    user_id = str(user_info.get("user_id", ""))
    r = await _get_redis()

    # Update history entry
    raw_hist = await r.get(_history_key(user_id))
    history = json.loads(raw_hist) if raw_hist else []
    for h in history:
        if h.get("agent_id") == record.agent_id and h.get("outcome") == "OPEN":
            h["outcome"] = record.outcome or "OPEN"
            h["pnl"] = record.pnl
            break
    await r.set(_history_key(user_id), json.dumps(history))

    # Update agent stats
    raw_ag = await r.get(_agent_key(user_id))
    agents = json.loads(raw_ag) if raw_ag else []
    for ag in agents:
        if ag["id"] == record.agent_id:
            if record.pnl is not None:
                ag["pnl"] = round(ag.get("pnl", 0) + record.pnl, 2)
            if record.outcome == "WIN":
                ag["wins"] = ag.get("wins", 0) + 1
            elif record.outcome == "LOSS":
                ag["losses"] = ag.get("losses", 0) + 1
            total = ag.get("wins", 0) + ag.get("losses", 0)
            ag["winrate"] = round(ag["wins"] / total * 100) if total > 0 else 0
            # Auto-disable if winrate < 40% after 5+ trades
            if total >= 5 and ag["winrate"] < 40:
                ag["status"] = "DISABLED"
            # Auto-disable if drawdown > 8% (pnl < -80 proxy)
            if ag.get("pnl", 0) < -80:
                ag["status"] = "DISABLED"
            break
    await r.set(_agent_key(user_id), json.dumps(agents))
    return {"status": "ok"}
