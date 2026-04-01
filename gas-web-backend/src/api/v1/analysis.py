"""
GAS Analysis API — All 18 AI Features
Calls gas-strategy-core for real AI-powered analysis.
Admin users bypass credit deduction entirely.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from ...core.dependencies import get_current_user, get_current_user_info
import httpx
import os
import json
import uuid
import redis.asyncio as aioredis
from datetime import datetime, timezone
from .billing import deduct_credits, get_user_credits, reserve_credits, confirm_reservation, release_credits
from ...services.circuit_breaker import CircuitBreakerRegistry, CircuitOpenError

router = APIRouter(tags=["AI Analysis Features"])

# Style → Timeframe Matrix per spec update18fiture_v1.01.md
STYLE_MATRIX = {
    "scalping": {"tfs": ["H4", "H1", "M15", "M5"],  "roles": ["Macro", "Narrative", "Setup", "Execution"]},
    "intraday": {"tfs": ["D1", "H4", "H1", "M15"], "roles": ["Macro", "Narrative", "Setup", "Execution"]},
    "swing":    {"tfs": ["W1", "D1", "H4", "H1"],  "roles": ["Macro", "Narrative", "Setup", "Execution"]},
}

def _resolve_timeframe(style: str, timeframe: str) -> tuple[str, list]:
    """Resolve primary TF and TF matrix from style. If no style, use provided timeframe."""
    if style and style in STYLE_MATRIX:
        tfs = STYLE_MATRIX[style]["tfs"]
        primary = tfs[2]  # Setup TF
        return primary, tfs
    return timeframe or "H1", []

FEATURE_CREDIT_COST = {
    "technical": 3, "signal": 3, "alert": 1, "session": 1,
    "correlation": 3, "scanner": 15, "fundamental": 5,
    "calendar": 4, "sentiment": 5, "briefing": 10,
    "hybrid": 8, "risk": 3, "drawdown": 5, "backtesting": 20,
    "psychology": 5, "journal": 8, "mentor": 10, "propfirm": 8,
}

MARKET_MULTIPLIER = {
    "forex":    1.0,
    "crypto":   1.2,
    "stock":    1.3,
    "meme":     1.5,
    "poly":     1.2,
    "binance":  1.2,
}

def _get_credit_cost(feature: str, market: str = "forex") -> int:
    base = FEATURE_CREDIT_COST.get(feature, 3)
    mult = MARKET_MULTIPLIER.get(market, 1.0)
    return max(1, int(base * mult))

STRATEGY_CORE_URL  = os.getenv("STRATEGY_CORE_URL", "http://gas-strategy-core:7003")
KIMI_API_KEY       = os.getenv("KIMI_API_KEY_ANALYSIS", "sk-4wPbTf8cQzNx6yc1t5FjzFkiUUMLOJ9IAYwX8HJstpAjoVYN")
KIMI_BASE_URL      = "https://api.moonshot.cn/v1"
KIMI_MODEL         = "moonshot-v1-8k"
REDIS_URL          = os.getenv("REDIS_URL", "redis://gas-redis:6379/0")

_redis = None
async def _get_redis():
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis


async def _store_analysis_history(user_id: str, feature: str, pair: str, summary: str, data: dict):
    """Store analysis result in Redis history (newest first, max 50 per user)."""
    try:
        r = await _get_redis()
        entry = {
            "id": str(uuid.uuid4()),
            "feature": feature,
            "pair": pair,
            "summary": summary[:200],
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        await r.lpush(f"analysis_history:{user_id}", json.dumps(entry))
        await r.ltrim(f"analysis_history:{user_id}", 0, 49)  # keep last 50
    except Exception:
        pass  # Don't fail the main request if history storage fails


async def _kimi_fallback(feature: str, payload: dict) -> dict:
    """Call Kimi AI (Moonshot) when strategy-core is unavailable."""
    pair = payload.get("pair", "XAUUSD")
    tf   = payload.get("timeframe", "H1")
    prompt = (
        f"Kamu adalah AI trading analyst profesional untuk platform Golden AI Strategy.\n"
        f"Feature: {feature}\nPair: {pair}\nTimeframe: {tf}\n"
        f"Data: {payload}\n\n"
        f"Berikan analisis {feature} yang akurat, actionable, dalam Bahasa Indonesia. "
        f"Format: ringkas, jelas, berikan rekomendasi konkret."
    )
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{KIMI_BASE_URL}/chat/completions",
                json={
                    "model": KIMI_MODEL,
                    "max_tokens": 1024,
                    "messages": [
                        {"role": "system", "content": "Kamu adalah AI trading analyst expert platform GAS (Golden AI Strategy). Jawab dalam Bahasa Indonesia, profesional, ringkas, dan actionable."},
                        {"role": "user", "content": prompt},
                    ],
                },
                headers={"Authorization": f"Bearer {KIMI_API_KEY}", "Content-Type": "application/json"},
            )
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                return {"result": {"summary": content}, "source": "kimi-ai-fallback", "pair": pair}
    except Exception:
        pass
    return {"result": {"summary": f"Analisis {feature} untuk {pair} tidak tersedia. Pastikan service aktif."}, "source": "offline"}


class FeatureRequest(BaseModel):
    pair: Optional[str] = "XAUUSD"
    style: Optional[str] = "scalping"   # scalping | intraday | swing
    timeframe: Optional[str] = "H1"
    params: Optional[Dict[str, Any]] = {}

class TechnicalRequest(FeatureRequest):
    indicators: Optional[List[str]] = ["RSI", "MACD", "ADX", "BB", "EMA"]

class HybridRequest(FeatureRequest):
    pass

class PsychologyRequest(BaseModel):
    emotion: str
    risks: Optional[List[str]] = []
    recent_pnl: Optional[str] = ""

class BriefingRequest(BaseModel):
    type: Optional[str] = "daily"

class RiskRequest(BaseModel):
    balance: Optional[float] = None
    risk_pct: Optional[float] = 1.0
    pair: Optional[str] = "XAUUSD"
    sl_pips: Optional[float] = None

class SignalRequest(BaseModel):
    pair: Optional[str] = "XAUUSD"
    style: Optional[str] = "scalping"   # scalping | intraday | swing
    timeframe: Optional[str] = "H1"
    model_tier: Optional[str] = "basic"   # basic | advanced | pro | ultra | gpt | agent
    market: Optional[str] = "forex"      # forex | crypto | stock | meme | poly | binance

class ScannerRequest(BaseModel):
    pairs: Optional[List[str]] = []
    style: Optional[str] = "scalping"   # scalping | intraday | swing
    timeframe: Optional[str] = "H4"
    min_confluence: Optional[int] = 60
    model_tier: Optional[str] = "basic"   # basic | advanced | pro | ultra | gpt | grok

# ── Model Tier Config (mirrors gas-strategy-core openrouter.py) ────────────────
MODEL_TIERS = {
    "basic":    {"min_plan": "essential", "signal_cost": 1,  "scanner_cost": 5,  "label": "GAS Basic",    "badge": "V3",    "model": "DeepSeek V3"},
    "advanced": {"min_plan": "plus",      "signal_cost": 2,  "scanner_cost": 8,  "label": "GAS Advanced", "badge": "FLASH", "model": "Gemini Flash"},
    "pro":      {"min_plan": "premium",   "signal_cost": 3,  "scanner_cost": 12, "label": "GAS Pro",      "badge": "HAIKU", "model": "Claude Haiku"},
    "ultra":    {"min_plan": "ultimate",  "signal_cost": 5,  "scanner_cost": 18, "label": "GAS Ultra",    "badge": "SONNET","model": "Claude Sonnet 4.6"},
    "gpt":      {"min_plan": "ultimate",  "signal_cost": 5,  "scanner_cost": 18, "label": "GAS GPT",      "badge": "GPT",   "model": "GPT-4o"},
    "agent":    {"min_plan": "ultra",     "signal_cost": 10, "scanner_cost": 25, "label": "GAS Agent",    "badge": "AGENT", "model": "Claude Opus 4.6"},
}
PLAN_ORDER = ["essential", "plus", "premium", "ultimate", "ultra"]

async def _get_user_plan(user_id: str) -> str:
    """Read user's subscription plan from Redis."""
    try:
        r = await _get_redis()
        plan = await r.get(f"user:{user_id}:plan")
        return plan or "essential"
    except Exception:
        return "essential"

async def _validate_model_tier(user_id: str, is_admin: bool, model_tier: str) -> str:
    """Validate model tier against user's plan. Returns validated tier."""
    if is_admin:
        return model_tier
    tier_cfg = MODEL_TIERS.get(model_tier)
    if not tier_cfg:
        return "basic"
    user_plan = await _get_user_plan(user_id)
    required_plan = tier_cfg["min_plan"]
    user_rank = PLAN_ORDER.index(user_plan) if user_plan in PLAN_ORDER else 0
    required_rank = PLAN_ORDER.index(required_plan) if required_plan in PLAN_ORDER else 0
    if user_rank >= required_rank:
        return model_tier
    # Downgrade to highest available tier
    best = "basic"
    for t, cfg in MODEL_TIERS.items():
        req_rank = PLAN_ORDER.index(cfg["min_plan"]) if cfg["min_plan"] in PLAN_ORDER else 0
        if user_rank >= req_rank:
            best = t
    return best

class AlertRequest(BaseModel):
    pair: Optional[str] = "XAUUSD"
    condition: Optional[str] = "signal_buy"   # signal_buy | signal_sell | price_above | price_below
    value: Optional[float] = None

class MentorRequest(BaseModel):
    pair: Optional[str] = "XAUUSD"
    timeframe: Optional[str] = "H1"
    question: Optional[str] = ""

class BacktestRequest(BaseModel):
    pair: Optional[str] = "XAUUSD"
    timeframe: Optional[str] = "H1"
    lookback: Optional[int] = 300
    rr_ratio: Optional[float] = 2.0


async def _call_core_raw(endpoint: str, payload: dict, timeout: int = 45) -> dict:
    """Direct HTTP call to gas-strategy-core — used inside circuit breaker."""
    async with httpx.AsyncClient(timeout=timeout) as client:
        res = await client.post(f"{STRATEGY_CORE_URL}{endpoint}", json=payload)
        res.raise_for_status()
        return res.json()


async def _call_core(endpoint: str, payload: dict, timeout: int = 45) -> dict:
    """
    Call gas-strategy-core through a per-endpoint circuit breaker.
    Each endpoint has its own breaker — a noisy /briefing endpoint won't
    block healthy /signal or /technical endpoints.
    """
    cb_key = f"strategy-core:{endpoint}"
    cb = CircuitBreakerRegistry.get(cb_key, failure_threshold=5, recovery_timeout=60.0)
    try:
        return await cb.call(_call_core_raw, endpoint, payload, timeout=timeout)
    except CircuitOpenError as e:
        raise HTTPException(status_code=503, detail=f"strategy-core circuit open: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"strategy-core error: {e.response.text}")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="strategy-core timeout — EA mungkin tidak mengirim data")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"strategy-core unavailable: {str(e)}")


def _normalize_result(feature: str, data: dict) -> dict:
    """
    Ensure every response has a `result.summary` field that the frontend can read.
    Extracts the most meaningful field from each strategy-core response shape.
    """
    if data.get("result") and isinstance(data["result"], dict) and data["result"].get("summary"):
        return data  # already normalized

    summary = ""
    pair = data.get("pair", "XAUUSD")

    if feature == "signal":
        sig_type  = data.get("signal", "NEUTRAL")
        conf      = data.get("probability", 0)
        entry     = data.get("entry", "")
        sl        = data.get("sl", "")
        tp1       = data.get("tp1", "")
        summary   = (f"Signal: {sig_type} ({conf}% confidence). "
                     f"Entry: {entry} | SL: {sl} | TP1: {tp1}")

    elif feature == "fundamental":
        ai_analysis = data.get("ai_analysis", "")
        macro       = data.get("macro_data", {})
        if isinstance(ai_analysis, str) and ai_analysis:
            summary = ai_analysis
        elif isinstance(macro, dict):
            summary = f"Fundamental data loaded. CPI: {macro.get('cpi_us','N/A')}, Fed Rate: {macro.get('fed_rate','N/A')}"
        else:
            summary = "Data fundamental berhasil diambil."

    elif feature == "calendar":
        events     = data.get("events", [])
        hi_count   = data.get("high_impact_count", 0)
        source     = data.get("source", "")
        ev_titles  = ", ".join(e.get("title", e.get("name","?")) for e in events[:3]) if events else "Tidak ada event hari ini"
        summary    = f"{hi_count} high-impact event hari ini: {ev_titles}. Source: {source}"

    elif feature == "sentiment":
        fg         = data.get("fear_greed", {})
        ai_signal  = data.get("ai_signal", "")
        score      = fg.get("value", fg.get("score", "?")) if isinstance(fg, dict) else fg
        label      = fg.get("classification", "") if isinstance(fg, dict) else ""
        summary    = f"Fear & Greed: {score} ({label}). AI Signal: {ai_signal}"

    elif feature == "briefing":
        ai_brief   = data.get("ai_briefing", "")
        macro_sum  = data.get("macro_summary", "")
        summary    = ai_brief or macro_sum or "Daily briefing generated."

    elif feature == "risk":
        lot        = data.get("recommended_lot", data.get("lot_size", ""))
        risk_usd   = data.get("risk_amount_usd", data.get("risk_amount", ""))
        alert      = data.get("alert", "")
        heat       = data.get("portfolio_heat", "")
        summary    = (f"Rekomendasi lot: {lot} | Risk USD: ${risk_usd} | "
                      f"Portfolio heat: {heat}% | {alert}")

    elif feature == "drawdown":
        dd_pct     = data.get("current_dd_pct", data.get("drawdown_pct", 0))
        dd_active  = data.get("dd_mode", False)
        dd_label   = "DRAWDOWN AKTIF" if dd_active else "NORMAL"
        plan       = data.get("recovery_plan", [])
        reduction  = data.get("risk_reduction", 0)
        plan_str   = "; ".join(plan[:2]) if isinstance(plan, list) else str(plan)
        summary    = (f"Drawdown saat ini: {float(dd_pct):.1f}% ({dd_label}). "
                      f"Risk reduction: {reduction}%. {plan_str}")

    elif feature == "correlation":
        matrix     = data.get("correlation_matrix", {})
        n_pairs    = len(data.get("symbols_used", matrix.keys() if isinstance(matrix, dict) else []))
        candles    = data.get("candles_used", "?")
        top        = ""
        if isinstance(matrix, dict) and pair in matrix:
            others = {k: v for k, v in matrix[pair].items() if k != pair}
            if others:
                top_pair = max(others, key=lambda x: abs(others[x]))
                top = f" | Korelasi tertinggi: {top_pair} ({others[top_pair]:.2f})"
        summary    = f"Korelasi {n_pairs} pair | {candles} candles{top}"

    elif feature == "psychology":
        coaching   = data.get("ai_coaching", data.get("coaching", ""))
        emotion    = data.get("emotion", "")
        score      = data.get("emotion_score", "")
        safe       = data.get("safe_to_trade", True)
        summary    = coaching or f"Emosi: {emotion} (score {score}). {'Aman trading.' if safe else 'Hindari trading saat ini.'}"

    elif feature == "journal":
        insights   = data.get("insights", data.get("ai_review", data.get("ai_feedback", "")))
        n_trades   = data.get("total_trades", data.get("trade_count", "?"))
        win_rate   = data.get("win_rate", "")
        msg        = data.get("message", data.get("note", ""))
        if insights:
            summary = insights
        elif msg:
            summary = msg
        else:
            summary = f"Jurnal AI: {n_trades} trade | Win rate: {win_rate}. Hubungkan MT5 EA untuk analisis lengkap."

    elif feature == "mentor":
        # strategy-core returns 'mentor_review' field
        response   = data.get("mentor_review", data.get("response", data.get("mentor_reply", data.get("ai_response", ""))))
        summary    = response or "Mentor sedang menganalisis pertanyaan Anda."

    elif feature == "alert":
        # strategy-core returns alert_id, note, alert_created
        created    = data.get("alert_created", True)
        alert_id   = data.get("alert_id", "")
        note       = data.get("note", "")
        warn       = data.get("warning", "")
        status     = "dibuat" if created else "gagal"
        summary    = note or f"Alert {status} untuk {pair}. {warn or ''} ID: {alert_id}"

    elif feature == "backtesting":
        n_trades   = data.get("total_trades", 0)
        win_rate   = data.get("win_rate", "N/A")
        profit_f   = data.get("profit_factor", "N/A")
        net        = data.get("net_profit_usd", data.get("net_profit", "N/A"))
        msg        = data.get("message", "")
        if n_trades == 0:
            summary = msg or f"Backtest {pair}: tidak ada trade signal memenuhi threshold."
        else:
            summary = (f"Backtest {pair}: {n_trades} trades | WR: {win_rate}% | "
                       f"PF: {profit_f} | Net: ${net}")

    elif feature == "scanner":
        qualified  = data.get("qualified", 0)
        scanned    = data.get("scanned", 0)
        ai_sum     = data.get("ai_summary", "")
        top_pick   = data.get("top_pick", {})
        top_sym    = top_pick.get("symbol", "") if isinstance(top_pick, dict) else ""
        summary    = ai_sum or f"Scanner: {qualified}/{scanned} pair qualified. Top: {top_sym}"

    else:
        # Fallback: grab any string field
        for key in ("summary", "recommendation", "advice", "result", "detail", "message"):
            val = data.get(key, "")
            if isinstance(val, str) and val:
                summary = val
                break
        if not summary:
            summary = f"Analisis {feature} untuk {pair} selesai."

    # Inject normalized result if missing
    if "result" not in data or not isinstance(data.get("result"), dict):
        data["result"] = {"summary": summary}
    elif not data["result"].get("summary"):
        data["result"]["summary"] = summary

    return data


async def _call_core_with_credits(
    endpoint: str,
    payload: dict,
    feature: str,
    user_info: dict,
    model_tier: str = "basic",
) -> dict:
    """
    Atomic credit deduction: RESERVE → execute → CONFIRM (success) | RELEASE (failure).
    Credits are NEVER lost if strategy-core times out or errors.
    model_tier controls the reservation TTL (heavy models get longer TTL).
    """
    user_id  = user_info["user_id"]
    is_admin = user_info["is_admin"]
    cost     = FEATURE_CREDIT_COST.get(feature, 3)

    # ── RESERVE ─────────────────────────────────────────────────────────────────
    reservation_id = await reserve_credits(user_id, cost, is_admin=is_admin, model_tier=model_tier)
    if reservation_id is None:
        remaining = await get_user_credits(user_id)
        raise HTTPException(
            status_code=402,
            detail=f"Kredit tidak cukup. Butuh {cost} cr, tersisa {remaining} cr. Top-up di halaman Pricing.",
        )

    # ── EXECUTE ──────────────────────────────────────────────────────────────────
    try:
        try:
            data = await _call_core(endpoint, payload)
            data = _normalize_result(feature, data)
        except HTTPException as e:
            if e.status_code in (503, 504, 404):
                # Fallback to Kimi AI — normalize to same contract as strategy-core
                data = await _kimi_fallback(feature, payload)
                data = _normalize_result(feature, data)  # ensure same shape for frontend
            else:
                raise

        # ── CONFIRM (credits consumed) ───────────────────────────────────────────
        await confirm_reservation(reservation_id)

    except HTTPException:
        # ── RELEASE (credits refunded) ───────────────────────────────────────────
        await release_credits(reservation_id)
        raise
    except Exception as exc:
        await release_credits(reservation_id)
        raise HTTPException(status_code=503, detail=f"Operasi gagal — kredit dikembalikan: {exc}")

    remaining = await get_user_credits(user_id, is_admin)
    data["credits_used"]      = 0 if is_admin else cost
    data["credits_remaining"] = remaining

    # Store in history
    pair    = payload.get("pair", "XAUUSD")
    summary = data.get("result", {}).get("summary", "") if isinstance(data.get("result"), dict) else ""
    await _store_analysis_history(user_id, feature, pair, summary, data)

    return data


# ── Static GET routes MUST come before /{analysis_id} wildcard ────────────────

@router.get("/history")
async def get_analysis_history(
    limit: int = 20,
    user_info: dict = Depends(get_current_user_info),
):
    """Return recent analysis history for this user from Redis."""
    user_id = user_info["user_id"]
    r = await _get_redis()
    raw_list = await r.lrange(f"analysis_history:{user_id}", 0, limit - 1)
    entries = []
    for raw in raw_list:
        try:
            entries.append(json.loads(raw))
        except Exception:
            pass
    return {"history": entries, "total": len(entries)}


@router.get("/signal/models")
async def get_signal_models(user_info: dict = Depends(get_current_user_info)):
    """Return available AI model tiers with user's plan access."""
    user_id = user_info["user_id"]
    is_admin = user_info["is_admin"]
    user_plan = await _get_user_plan(user_id) if not is_admin else "ultimate"
    user_rank = PLAN_ORDER.index(user_plan) if user_plan in PLAN_ORDER else 0

    models = []
    for tier_id, cfg in MODEL_TIERS.items():
        req_rank = PLAN_ORDER.index(cfg["min_plan"]) if cfg["min_plan"] in PLAN_ORDER else 0
        models.append({
            "tier": tier_id,
            "label": cfg["label"],
            "min_plan": cfg["min_plan"],
            "signal_cost": cfg["signal_cost"],
            "scanner_cost": cfg["scanner_cost"],
            "unlocked": is_admin or user_rank >= req_rank,
        })
    return {"models": models, "user_plan": user_plan}


@router.get("/{analysis_id}")
async def get_analysis_detail(analysis_id: str, user_info: dict = Depends(get_current_user_info)):
    """Look up a specific analysis entry by ID from history."""
    user_id = user_info["user_id"]
    r = await _get_redis()
    raw_list = await r.lrange(f"analysis_history:{user_id}", 0, -1)
    for raw in raw_list:
        try:
            entry = json.loads(raw)
            if entry.get("id") == analysis_id:
                return entry
        except Exception:
            pass
    raise HTTPException(status_code=404, detail="Analysis record not found")


# ── All 18 Feature Endpoints ──────────────────────────────────────────────────

@router.post("/technical")
async def analyze_technical(req: TechnicalRequest, user_info: dict = Depends(get_current_user_info)):
    primary_tf, tf_matrix = _resolve_timeframe(req.style or "", req.timeframe or "H1")
    # pure_compute=True: skip LLM → rule-based output, faster + cheaper
    # pure_compute=False: full AI narrative (still used by premium features as sub-call)
    use_pure = req.params.get("pure_compute", True) if req.params else True
    data = await _call_core_with_credits("/v1/analysis/technical", {
        "pair": req.pair, "timeframe": primary_tf,
        "style": req.style or "scalping",
        "timeframe_matrix": tf_matrix,
        "indicators": req.indicators, "user_id": user_info["user_id"],
        "pure_compute": use_pure,
    }, "technical", user_info)
    return {"feature": "technical", "credit_cost": FEATURE_CREDIT_COST["technical"], "style": req.style, "tf_matrix": tf_matrix, **data}


@router.post("/signal")
async def generate_signal(req: SignalRequest, user_info: dict = Depends(get_current_user_info)):
    user_id = user_info["user_id"]
    is_admin = user_info["is_admin"]

    # Validate tier against user's plan
    tier = await _validate_model_tier(user_id, is_admin, req.model_tier or "basic")
    tier_cfg = MODEL_TIERS[tier]
    market = req.market or "forex"
    base_cost = tier_cfg["signal_cost"]
    # Override with tier-specific cost if higher
    cost = 0 if is_admin else max(base_cost, _get_credit_cost("signal", market))

    # Deduct credits
    success, remaining = await deduct_credits(user_id, cost, is_admin=is_admin)
    if not success:
        raise HTTPException(
            status_code=402,
            detail=f"Kredit tidak cukup untuk {tier_cfg['label']}. Butuh {cost} cr, tersisa {remaining} cr."
        )

    # Call strategy-core with tier — use longer timeout for premium models
    heavy_tiers = {"ultra", "gpt", "agent"}
    core_timeout = 120 if tier in heavy_tiers else 60
    try:
        primary_tf, tf_matrix = _resolve_timeframe(req.style or "", req.timeframe or "H1")
        data = await _call_core("/v1/analysis/signal", {
            "pair": req.pair, "timeframe": primary_tf,
            "style": req.style or "scalping",
            "timeframe_matrix": tf_matrix,
            "model_tier": tier, "user_id": user_id,
            "market": req.market or "forex",
        }, timeout=core_timeout)
        data = _normalize_result("signal", data)
    except HTTPException as e:
        if e.status_code in (503, 504, 404):
            data = await _kimi_fallback("signal", {"pair": req.pair, "timeframe": req.timeframe, "style": req.style})
            data = _normalize_result("signal", data)
        else:
            raise

    data["credits_used"] = cost
    data["credits_remaining"] = remaining
    data["model_tier"] = tier
    data["model_label"] = tier_cfg["label"]

    pair = req.pair or "XAUUSD"
    summary = data.get("result", {}).get("summary", "") if isinstance(data.get("result"), dict) else ""
    await _store_analysis_history(user_id, "signal", pair, summary, data)

    return {"feature": "signal", "credit_cost": cost, "model_tier": tier, **data}


@router.post("/session")
async def session_optimizer(req: FeatureRequest, user_info: dict = Depends(get_current_user_info)):
    user_id = user_info["user_id"]
    is_admin = user_info["is_admin"]
    cost = FEATURE_CREDIT_COST["session"]
    success, remaining = await deduct_credits(user_id, cost, is_admin=is_admin)
    if not success:
        raise HTTPException(status_code=402, detail=f"Kredit tidak cukup. Butuh {cost} cr, tersisa {remaining} cr.")

    # Session optimizer uses server time (UTC+7 WIB)
    from datetime import timezone, timedelta
    wib = timezone(timedelta(hours=7))
    now = datetime.now(wib)
    hour = now.hour
    sessions = [
        {"name": "Asian",   "time": "07:00-09:00 WIB", "active": 7 <= hour < 9,   "volatility": "LOW",     "score": 45},
        {"name": "London",  "time": "14:00-17:00 WIB", "active": 14 <= hour < 17,  "volatility": "HIGH",    "score": 88},
        {"name": "NY",      "time": "19:00-22:00 WIB", "active": 19 <= hour < 22,  "volatility": "HIGH",    "score": 82},
        {"name": "Overlap", "time": "19:00-21:00 WIB", "active": 19 <= hour < 21,  "volatility": "EXTREME", "score": 95},
    ]
    active = [s for s in sessions if s["active"]]
    best = max(sessions, key=lambda x: x["score"])
    current = active[0]["name"] if active else "OFF-HOURS"
    summary = f"Sesi aktif: {current}. Best session untuk {req.pair}: {best['name']} (score {best['score']}/100). {best.get('volatility','HIGH')} volatility."
    return {
        "feature": "session", "credit_cost": FEATURE_CREDIT_COST["session"],
        "pair": req.pair, "current_session": current,
        "best_session": best["name"], "sessions": sessions,
        "recommendation": summary,
        "result": {"summary": summary, "current_session": current, "best_session": best["name"]},
        "credits_used": 0 if is_admin else cost, "credits_remaining": remaining,
    }


@router.post("/correlation")
async def correlation_tracker(req: FeatureRequest, user_info: dict = Depends(get_current_user_info)):
    data = await _call_core_with_credits("/v1/analysis/correlation", {
        "pair": req.pair, "timeframe": req.timeframe or "H1", "user_id": user_info["user_id"],
    }, "correlation", user_info)
    return {"feature": "correlation", "credit_cost": FEATURE_CREDIT_COST["correlation"], **data}


@router.post("/alert")
async def smart_alert(req: AlertRequest, user_info: dict = Depends(get_current_user_info)):
    data = await _call_core_with_credits("/v1/analysis/alert", {
        "pair": req.pair, "condition": req.condition,
        "value": req.value, "user_id": user_info["user_id"],
    }, "alert", user_info)
    return {"feature": "alert", "credit_cost": FEATURE_CREDIT_COST["alert"], **data}


@router.post("/fundamental")
async def fundamental_analysis(req: FeatureRequest, user_info: dict = Depends(get_current_user_info)):
    data = await _call_core_with_credits("/v1/analysis/fundamental", {
        "pair": req.pair, "timeframe": req.timeframe, "user_id": user_info["user_id"],
    }, "fundamental", user_info)
    return {"feature": "fundamental", "credit_cost": FEATURE_CREDIT_COST["fundamental"], **data}


@router.post("/calendar")
async def economic_calendar(req: BriefingRequest, user_info: dict = Depends(get_current_user_info)):
    data = await _call_core_with_credits("/v1/analysis/calendar", {
        "type": req.type or "daily", "user_id": user_info["user_id"],
    }, "calendar", user_info)
    return {"feature": "calendar", "credit_cost": FEATURE_CREDIT_COST["calendar"], **data}


@router.post("/sentiment")
async def sentiment_analysis(req: FeatureRequest, user_info: dict = Depends(get_current_user_info)):
    data = await _call_core_with_credits("/v1/analysis/sentiment", {
        "pair": req.pair, "user_id": user_info["user_id"],
    }, "sentiment", user_info)
    return {"feature": "sentiment", "credit_cost": FEATURE_CREDIT_COST["sentiment"], **data}


@router.post("/briefing")
async def market_briefing(req: BriefingRequest, user_info: dict = Depends(get_current_user_info)):
    data = await _call_core_with_credits("/v1/analysis/briefing", {
        "type": req.type or "daily", "user_id": user_info["user_id"],
    }, "briefing", user_info)
    return {"feature": "briefing", "credit_cost": FEATURE_CREDIT_COST["briefing"], **data}


@router.post("/hybrid")
async def hybrid_analysis(req: HybridRequest, user_info: dict = Depends(get_current_user_info)):
    data = await _call_core_with_credits("/v1/analysis/hybrid", {
        "pair": req.pair, "timeframe": req.timeframe, "user_id": user_info["user_id"],
    }, "hybrid", user_info)
    return {"feature": "hybrid", "credit_cost": FEATURE_CREDIT_COST["hybrid"], **data}


@router.post("/risk")
async def risk_manager(req: RiskRequest, user_info: dict = Depends(get_current_user_info)):
    data = await _call_core_with_credits("/v1/analysis/risk", {
        "user_id": user_info["user_id"], "balance": req.balance,
        "risk_pct": req.risk_pct, "pair": req.pair, "sl_pips": req.sl_pips,
    }, "risk", user_info)
    return {"feature": "risk", "credit_cost": FEATURE_CREDIT_COST["risk"], **data}


@router.post("/drawdown")
async def drawdown_recovery(req: FeatureRequest, user_info: dict = Depends(get_current_user_info)):
    payload = {
        "user_id": user_info["user_id"],
        "pair": req.pair,
        "timeframe": req.timeframe,
    }
    # Merge extra params (balance, equity, drawdown_pct) sent from frontend
    if req.params:
        payload.update(req.params)
    data = await _call_core_with_credits("/v1/analysis/drawdown", payload, "drawdown", user_info)
    return {"feature": "drawdown", "credit_cost": FEATURE_CREDIT_COST["drawdown"], **data}


@router.post("/backtesting")
async def backtesting_engine(req: BacktestRequest, user_info: dict = Depends(get_current_user_info)):
    data = await _call_core_with_credits("/v1/analysis/backtesting", {
        "pair": req.pair, "timeframe": req.timeframe,
        "lookback": req.lookback or 300, "rr_ratio": req.rr_ratio or 2.0,
        "user_id": user_info["user_id"],
    }, "backtesting", user_info)
    return {"feature": "backtesting", "credit_cost": FEATURE_CREDIT_COST["backtesting"], **data}


@router.post("/psychology")
async def psychology_coach(req: PsychologyRequest, user_info: dict = Depends(get_current_user_info)):
    data = await _call_core_with_credits("/v1/analysis/psychology", {
        "emotion": req.emotion, "risks": req.risks,
        "recent_pnl": req.recent_pnl, "user_id": user_info["user_id"],
    }, "psychology", user_info)
    return {"feature": "psychology", "credit_cost": FEATURE_CREDIT_COST["psychology"], **data}


@router.post("/journal")
async def ai_journal_review(req: FeatureRequest, user_info: dict = Depends(get_current_user_info)):
    payload = {"user_id": user_info["user_id"], "pair": req.pair}
    # Forward trade history if provided in params
    if req.params:
        payload.update(req.params)
    data = await _call_core_with_credits("/v1/analysis/journal", payload, "journal", user_info)
    return {"feature": "journal", "credit_cost": FEATURE_CREDIT_COST["journal"], **data}


@router.post("/mentor")
async def ai_mentor_mode(req: MentorRequest, user_info: dict = Depends(get_current_user_info)):
    data = await _call_core_with_credits("/v1/analysis/mentor", {
        "pair": req.pair, "timeframe": req.timeframe,
        "question": req.question or "", "user_id": user_info["user_id"],
    }, "mentor", user_info)
    return {"feature": "mentor", "credit_cost": FEATURE_CREDIT_COST["mentor"], **data}


@router.post("/propfirm")
async def propfirm_assistant(req: FeatureRequest, user_info: dict = Depends(get_current_user_info)):
    user_id = user_info["user_id"]
    is_admin = user_info["is_admin"]
    cost = FEATURE_CREDIT_COST["propfirm"]
    success, remaining = await deduct_credits(user_id, cost, is_admin=is_admin)
    if not success:
        raise HTTPException(status_code=402, detail=f"Kredit tidak cukup. Butuh {cost} cr, tersisa {remaining} cr.")
    # Fetch risk and drawdown data independently; graceful degradation if core is down
    risk_data = {}
    dd_data = {}
    try:
        risk_data = await _call_core("/v1/analysis/risk", {"user_id": user_id, "pair": req.pair, "risk_pct": 1.0})
    except Exception:
        risk_data = {"status": "unavailable", "detail": "strategy-core tidak tersedia"}
    try:
        dd_data = await _call_core("/v1/analysis/drawdown", {"user_id": user_id, "pair": req.pair})
    except Exception:
        dd_data = {"status": "unavailable", "detail": "strategy-core tidak tersedia"}
    return {
        "feature": "propfirm", "credit_cost": FEATURE_CREDIT_COST["propfirm"],
        "pair": req.pair,
        "account_risk": risk_data,
        "drawdown_status": dd_data,
        "prop_advice": "Data akun real dari MT5. Pastikan DD sesuai rules prop firm.",
        "result": {"summary": f"PropFirm check untuk {req.pair} selesai. Periksa account_risk dan drawdown_status."},
        "source": "real-data",
        "credits_used": 0 if is_admin else cost, "credits_remaining": remaining,
    }


@router.post("/scanner")
async def multi_symbol_scanner(req: ScannerRequest, user_info: dict = Depends(get_current_user_info)):
    user_id = user_info["user_id"]
    is_admin = user_info["is_admin"]

    # Validate tier against user's plan
    tier = await _validate_model_tier(user_id, is_admin, req.model_tier or "basic")
    tier_cfg = MODEL_TIERS[tier]
    cost = 0 if is_admin else tier_cfg["scanner_cost"]

    # Deduct credits
    success, remaining = await deduct_credits(user_id, cost, is_admin=is_admin)
    if not success:
        raise HTTPException(
            status_code=402,
            detail=f"Kredit tidak cukup untuk {tier_cfg['label']} Scanner. Butuh {cost} cr, tersisa {remaining} cr."
        )

    try:
        primary_tf, tf_matrix = _resolve_timeframe(req.style or "", req.timeframe or "H4")
        data = await _call_core("/v1/analysis/scanner", {
            "pairs": req.pairs or [], "timeframe": primary_tf,
            "style": req.style or "scalping",
            "timeframe_matrix": tf_matrix,
            "min_confluence": req.min_confluence,
            "model_tier": tier, "user_id": user_id,
        }, timeout=90)
        data = _normalize_result("scanner", data)
    except HTTPException as e:
        if e.status_code in (503, 504, 404):
            data = await _kimi_fallback("scanner", {"pairs": req.pairs, "timeframe": req.timeframe, "style": req.style})
            data = _normalize_result("scanner", data)
        else:
            raise

    data["credits_used"] = cost
    data["credits_remaining"] = remaining
    data["model_tier"] = tier
    data["model_label"] = tier_cfg["label"]

    await _store_analysis_history(user_id, "scanner", "multi-pair", str(data.get("qualified", 0)) + " qualified", data)

    return {"feature": "scanner", "credit_cost": cost, "model_tier": tier, **data}
