"""
gas-strategy-core — Real Data AI Engine
Fetches MT5 data from Redis + external APIs, runs DeepSeek AI analysis.
Auto-scheduler runs morning briefing at 06:30 WIB every day.
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import date

from src.core.engine import evaluate
from src.data.redis_mt5 import get_ohlc, get_ohlc_smart, get_latest_price, get_latest_price_smart, get_account, get_positions, get_all_symbols_with_data
from src.data.external import fetch_fear_greed, fetch_cot_gold, fetch_cot_dxy
from src.data.calendar import get_upcoming_events
from src.data.macro import get_macro_data
from src.data.smc_fetcher import run_smc_analysis, run_smc_scanner
from src.indicators.technical import compute_indicators
from src.ai import openrouter as ai

# ── Style → Multi-TF Matrix (DXY Correlation Methodology) ─────────────────────
# XAU bias MUST align with inverse DXY bias (DXY↑=XAU↓, DXY↓=XAU↑)
STYLE_TF_MATRIX = {
    "scalping": {"xau": ["H1", "M15", "M5", "M1"], "dxy": ["H1", "M15"]},
    "intraday": {"xau": ["H4", "H1", "M15", "M5"], "dxy": ["H4", "H1"]},
    "swing":    {"xau": ["D1", "H4", "H1", "M15"], "dxy": ["D1", "H4"]},
}
# DXY symbol names to try in MT5 (varies by broker)
DXY_SYMBOLS = ["USDX", "DXY", "DX", "US_DXY", "DXYUSD"]

# ── Feature Builder ────────────────────────────────────────────────────────────

def _detect_setup_type(indicators: dict, smc: dict | None) -> str:
    """
    Classify trading setup from indicator + SMC data.
    Returns: Pullback | Breakout | Reversal | Liquidity Grab | Continuation | Accumulation | Unknown
    """
    if not smc:
        rec = indicators.get("recommendation", "NEUTRAL")
        conf = indicators.get("confidence", 0)
        return "Continuation" if conf >= 60 else "Unknown"

    ms = smc.get("market_structure", {})
    liq = smc.get("liquidity", {})
    entry = smc.get("entry", {})
    time_ctx = smc.get("time_context", {})

    bias = ms.get("bias", "NEUTRAL")
    bos = ms.get("bos", [])
    choch = ms.get("choch", [])
    sweeps = liq.get("sweeps", [])
    ote = entry.get("ote", {})
    amd = time_ctx.get("amd_phase", "")

    rsi = indicators.get("RSI", {}).get("value", 50)
    adx = indicators.get("ADX", {}).get("value", 20)
    rec = indicators.get("recommendation", "NEUTRAL")

    # Reversal: CHoCH + overbought/oversold RSI
    if choch and (rsi > 72 or rsi < 28):
        return "Reversal"
    # Liquidity Grab: recent sweep + OTE zone + rejection
    if sweeps and ote.get("in_ote_zone"):
        return "Liquidity Grab"
    # Breakout: BOS + strong ADX + MACD bullish
    if bos and adx > 25 and rec in ("BUY", "SELL"):
        return "Breakout"
    # Pullback: bias is clear + price retracing to OTE
    if bias in ("BULLISH", "BEARISH") and ote.get("in_ote_zone") and not choch:
        return "Pullback"
    # Accumulation: AMD phase
    if "ACCUM" in amd.upper():
        return "Accumulation"
    # Continuation: strong trend, no structure break
    if bias in ("BULLISH", "BEARISH") and adx > 20 and not choch:
        return "Continuation"
    return "Unknown"


async def _build_feature_summary(
    symbol: str, timeframe: str, candles: list
) -> dict:
    """
    Feature Builder Layer — aggregates indicator + SMC engine output into
    compact feature summary. Saves ~90% tokens vs sending raw OHLC to AI.

    Returns enriched indicators dict with SMC context injected.
    """
    # 1. Compute technical indicators (inline — fast, no network)
    indicators = compute_indicators(candles)

    # 2. Fetch SMC analysis concurrently (uses gas-smc-engine)
    try:
        smc = await asyncio.wait_for(
            run_smc_analysis(symbol, timeframe, trading_style="intraday"),
            timeout=12.0,
        )
    except Exception:
        smc = None

    # 3. Detect setup type
    setup_type = _detect_setup_type(indicators, smc)

    # 4. Inject SMC features into indicators dict
    if smc:
        ms  = smc.get("market_structure", {})
        liq = smc.get("liquidity", {})
        zones = smc.get("zones", {})
        entry = smc.get("entry", {})
        time_ctx = smc.get("time_context", {})
        smc_sig = smc.get("signal", {})

        indicators["SMC"] = {
            "bias":          ms.get("bias", "NEUTRAL"),
            "structure":     ms.get("structure_type", ""),
            "bos":           len(ms.get("bos", [])) > 0,
            "choch":         len(ms.get("choch", [])) > 0,
            "order_blocks":  zones.get("order_blocks", [])[:2],  # top 2
            "fvg_count":     len(zones.get("fvgs", [])),
            "liquidity_swept": len(liq.get("sweeps", [])) > 0,
            "liquidity_pools": len(liq.get("pools", [])),
            "ote_zone":      entry.get("ote", {}).get("in_ote_zone", False),
            "ote_type":      entry.get("ote", {}).get("type", ""),
            "kill_zone":     time_ctx.get("in_kill_zone", False),
            "amd_phase":     time_ctx.get("amd_phase", ""),
            "session":       time_ctx.get("session_type", ""),
            "smc_score":     smc.get("confluence_score", 0),
            "smc_action":    smc_sig.get("action", "WAIT"),
            "smc_entry":     smc_sig.get("entry_price"),
            "smc_sl":        smc_sig.get("stop_loss"),
            "smc_tp":        smc_sig.get("take_profit"),
            "smc_rr":        smc_sig.get("rr"),
            "smc_reason":    smc_sig.get("reason", ""),
        }
        # Upgrade confluence score to include SMC
        ta_score = indicators.get("confidence", 50)
        smc_score = smc.get("confluence_score", 50)
        indicators["confluence_score"] = int((ta_score + smc_score) / 2)
    else:
        indicators["SMC"] = None
        indicators["confluence_score"] = indicators.get("confidence", 50)

    indicators["setup_type"] = setup_type
    return indicators


async def _get_dxy_candles(timeframe: str, limit: int = 100) -> list:
    """Try multiple DXY symbol names until one returns data."""
    for sym in DXY_SYMBOLS:
        try:
            candles = await get_ohlc(sym, timeframe, limit)
            if candles and len(candles) >= 20:
                return candles
        except Exception:
            pass
    return []


def _trend_from_indicators(ind: dict) -> str:
    """Derive trend label from indicator recommendations."""
    rec = ind.get("recommendation", "NEUTRAL")
    ema = ind.get("EMA", {})
    macd = ind.get("MACD", {})
    rsi_val = (ind.get("RSI") or {}).get("value", 50)
    if not isinstance(ema, dict):
        ema = {}
    if not isinstance(macd, dict):
        macd = {}
    # Require at least 2-indicator agreement
    bull = 0
    bear = 0
    if rec == "BUY":
        bull += 2
    elif rec == "SELL":
        bear += 2
    if ema.get("signal") == "BULLISH":
        bull += 1
    elif ema.get("signal") == "BEARISH":
        bear += 1
    if macd.get("signal") == "BULLISH":
        bull += 1
    elif macd.get("signal") == "BEARISH":
        bear += 1
    if rsi_val > 55:
        bull += 1
    elif rsi_val < 45:
        bear += 1
    if bull > bear + 1:
        return "BULLISH"
    if bear > bull + 1:
        return "BEARISH"
    return "NEUTRAL"


async def _compute_dxy_bias(dxy_tfs: list) -> dict:
    """
    Fetch DXY OHLC for given TFs, compute indicator trends.
    Returns: {tf: trend, ..., overall: BULLISH|BEARISH|NEUTRAL, available: bool}
    """
    result: dict = {"available": False, "overall": "NEUTRAL", "tfs": {}}
    bull_count = 0
    bear_count = 0
    for tf in dxy_tfs:
        candles = await _get_dxy_candles(tf, limit=100)
        if not candles:
            continue
        result["available"] = True
        ind = compute_indicators(candles)
        trend = _trend_from_indicators(ind)
        result["tfs"][tf] = {
            "trend": trend,
            "rsi": (ind.get("RSI") or {}).get("value"),
            "recommendation": ind.get("recommendation", "NEUTRAL"),
            "confidence": ind.get("confidence", 0),
        }
        if trend == "BULLISH":
            bull_count += 1
        elif trend == "BEARISH":
            bear_count += 1
    if bull_count > bear_count:
        result["overall"] = "BULLISH"
    elif bear_count > bull_count:
        result["overall"] = "BEARISH"
    return result


def _apply_dxy_correlation(xau_trend: str, dxy_overall: str) -> str:
    """
    DXY↑=XAU↓ (SELL), DXY↓=XAU↑ (BUY).
    Returns: CONFIRMED_BUY | CONFIRMED_SELL | CAUTION | NEUTRAL
    """
    if xau_trend == "BULLISH" and dxy_overall == "BEARISH":
        return "CONFIRMED_BUY"
    if xau_trend == "BEARISH" and dxy_overall == "BULLISH":
        return "CONFIRMED_SELL"
    if xau_trend == "BULLISH" and dxy_overall == "BULLISH":
        return "CAUTION_BUY"   # XAU bullish but DXY contradicts
    if xau_trend == "BEARISH" and dxy_overall == "BEARISH":
        return "CAUTION_SELL"  # XAU bearish but DXY contradicts
    return "NEUTRAL"


async def _build_mtf_features_with_dxy(
    symbol: str, style: str = "intraday"
) -> dict:
    """
    Multi-TF Feature Builder with DXY correlation.
    Returns aggregated feature dict:
    {
      mtf: {tf: {indicators, trend, price}, ...},
      dxy: {available, overall, tfs},
      correlation_signal: CONFIRMED_BUY|CONFIRMED_SELL|CAUTION|NEUTRAL,
      primary_tf: str,
      primary_features: dict (full indicator + SMC for primary TF),
    }
    """
    tf_cfg = STYLE_TF_MATRIX.get(style, STYLE_TF_MATRIX["intraday"])
    xau_tfs = tf_cfg["xau"]
    dxy_tfs = tf_cfg["dxy"]

    # Primary TF = second element (Setup TF)
    primary_tf = xau_tfs[1] if len(xau_tfs) > 1 else xau_tfs[0]

    # Fetch XAU data for all TFs + DXY in parallel
    xau_tasks = [(tf, asyncio.create_task(get_ohlc_smart(symbol, tf, 200))) for tf in xau_tfs]
    dxy_bias_task = asyncio.create_task(_compute_dxy_bias(dxy_tfs))

    mtf: dict = {}
    primary_features: dict = {}
    xau_trends: list = []

    for tf, task in xau_tasks:
        try:
            candles = await task
            if not candles or len(candles) < 20:
                continue
            if tf == primary_tf:
                # Full feature builder (indicator + SMC) for primary TF
                feat = await _build_feature_summary(symbol, tf, candles)
                primary_features = feat
                trend = _trend_from_indicators(feat)
            else:
                feat = compute_indicators(candles)
                trend = _trend_from_indicators(feat)
            xau_trends.append(trend)
            mtf[tf] = {
                "trend": trend,
                "price": feat.get("current_price"),
                "rsi": (feat.get("RSI") or {}).get("value"),
                "rsi_signal": (feat.get("RSI") or {}).get("signal", ""),
                "macd_signal": (feat.get("MACD") or {}).get("signal", ""),
                "ema_signal": (feat.get("EMA") or {}).get("signal", ""),
                "adx_value": (feat.get("ADX") or {}).get("value"),
                "adx_strength": (feat.get("ADX") or {}).get("strength", ""),
                "bb_position": (feat.get("BB") or {}).get("position", ""),
                "recommendation": feat.get("recommendation", "NEUTRAL"),
                "confidence": feat.get("confidence", 0),
                "smc_bias": ((feat.get("SMC") or {}).get("bias", "")) if tf == primary_tf else "",
                "smc_phase": ((feat.get("SMC") or {}).get("amd_phase", "")) if tf == primary_tf else "",
            }
        except Exception:
            pass

    dxy_bias = await dxy_bias_task

    # Overall XAU trend from all TFs (majority vote)
    bull = xau_trends.count("BULLISH")
    bear = xau_trends.count("BEARISH")
    xau_overall = "BULLISH" if bull > bear else ("BEARISH" if bear > bull else "NEUTRAL")

    correlation_signal = _apply_dxy_correlation(xau_overall, dxy_bias.get("overall", "NEUTRAL"))

    return {
        "mtf": mtf,
        "dxy": dxy_bias,
        "xau_overall": xau_overall,
        "correlation_signal": correlation_signal,
        "primary_tf": primary_tf,
        "primary_features": primary_features,
        "style": style,
    }


from src.cache import (
    get_cached_briefing, set_cached_briefing,
    get_cached_sentiment, set_cached_sentiment,
    get_cached_fundamental, get_cached_calendar,
)
from src.scheduler import start_scheduler, stop_scheduler, get_scheduler_status

log = logging.getLogger("gas.core")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start scheduler on startup, stop on shutdown."""
    log.info("gas-strategy-core starting up...")
    await start_scheduler(run_now=True)
    yield
    log.info("gas-strategy-core shutting down...")
    await stop_scheduler()


app = FastAPI(title="gas-strategy-core", version="3.0.0", lifespan=lifespan)


# ── Request Models ─────────────────────────────────────────────────────────────

class EvaluationRequest(BaseModel):
    strategy_name: str
    data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None

class TechnicalAnalysisRequest(BaseModel):
    pair: str = "XAUUSD"
    timeframe: str = "H1"
    indicators: Optional[List[str]] = ["RSI", "MACD", "ADX", "BB", "EMA"]
    user_id: Optional[str] = None
    pure_compute: bool = False   # Deprecated alias for compute_level="FAST"
    compute_level: Optional[str] = None  # FAST | STANDARD | FULL
    # FAST     = indicators only, no SMC call, no LLM → ~50ms latency
    # STANDARD = indicators + SMC structure, no LLM → ~200ms (default for pure_compute=True)
    # FULL     = indicators + SMC + LLM narrative → full AI response

class HybridAnalysisRequest(BaseModel):
    pair: str = "XAUUSD"
    timeframe: str = "H4"
    user_id: Optional[str] = None

class PsychologyRequest(BaseModel):
    emotion: str
    risks: Optional[List[str]] = []
    recent_pnl: Optional[str] = ""
    user_id: Optional[str] = None

class BriefingRequest(BaseModel):
    type: str = "daily"
    user_id: Optional[str] = None

class SentimentRequest(BaseModel):
    pair: str = "XAUUSD"
    user_id: Optional[str] = None

class ScannerRequest(BaseModel):
    pairs: Optional[List[str]] = []
    timeframe: str = "H4"
    min_confluence: int = 60
    model_tier: str = "basic"   # basic | advanced | pro | ultra
    user_id: Optional[str] = None

class SignalRequest(BaseModel):
    pair: str = "XAUUSD"
    timeframe: str = "H1"
    style: str = "intraday"     # scalping | intraday | swing
    model_tier: str = "basic"   # basic | advanced | pro | ultra | gpt | agent
    market: str = "forex"       # forex | crypto | stock | meme | poly
    timeframe_matrix: Optional[List[str]] = None
    user_id: Optional[str] = None

class RiskRequest(BaseModel):
    user_id: Optional[str] = None
    balance: Optional[float] = None
    risk_pct: Optional[float] = 1.0
    pair: Optional[str] = "XAUUSD"
    sl_pips: Optional[float] = None

class DrawdownRequest(BaseModel):
    user_id: Optional[str] = None
    pair: Optional[str] = "XAUUSD"


class CorrelationRequest(BaseModel):
    pair: str = "XAUUSD"
    timeframe: str = "H1"
    user_id: Optional[str] = None

class BacktestRequest(BaseModel):
    pair: str = "XAUUSD"
    timeframe: str = "H1"
    lookback: int = 300
    rr_ratio: float = 2.0
    user_id: Optional[str] = None

class JournalRequest(BaseModel):
    user_id: Optional[str] = None

class MentorRequest(BaseModel):
    pair: str = "XAUUSD"
    timeframe: str = "H1"
    question: Optional[str] = ""
    user_id: Optional[str] = None

class AlertRequest(BaseModel):
    pair: str = "XAUUSD"
    condition: str = "signal_buy"   # signal_buy | signal_sell | price_above | price_below
    value: Optional[float] = None
    user_id: Optional[str] = None

class SMCRequest(BaseModel):
    pair:          str            = "XAUUSD"
    timeframe:     str            = "H1"
    trading_style: str            = "intraday"   # scalping | intraday | swing
    user_id:       Optional[str]  = None


class SMCScannerRequest(BaseModel):
    pairs:         Optional[List[str]] = []
    timeframe:     str                 = "H4"
    trading_style: str                 = "swing"
    min_confluence: int                = 60
    user_id:       Optional[str]       = None


class AgentRequest(BaseModel):
    pair: str = "XAUUSD"
    timeframe: str = "M15"
    model: str = "claude"
    style: str = "scalping"
    min_confidence: int = 70
    max_trades: int = 2
    user_id: Optional[str] = None


# ── Health & Admin ────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "version": "3.0.0", "data": "real", "scheduler": "apscheduler"}


@app.get("/v1/signal/models")
def get_signal_models():
    """Return available AI model tiers for signal/scanner feature."""
    return {"models": ai.MODEL_TIERS}


@app.get("/v1/scheduler/status")
def scheduler_status():
    """Check scheduler status and next run times."""
    return get_scheduler_status()


@app.post("/v1/scheduler/trigger/{job_id}")
async def trigger_job(job_id: str, background_tasks: BackgroundTasks):
    """
    Manually trigger a scheduler job (admin use).
    job_id: morning_briefing | midday_refresh | weekly_briefing | sentiment | snapshot
    """
    from src.scheduler import job_morning_briefing, job_midday_refresh, job_fetch_sentiment, job_fetch_mt5_snapshot

    jobs = {
        "morning_briefing": job_morning_briefing,
        "midday_refresh": job_midday_refresh,
        "sentiment": job_fetch_sentiment,
        "snapshot": job_fetch_mt5_snapshot,
    }

    if job_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Unknown job: {job_id}. Available: {list(jobs.keys())}")

    background_tasks.add_task(jobs[job_id])
    return {"status": "triggered", "job": job_id, "note": "Running in background"}


# ── General AI Chat ───────────────────────────────────────────────────────────

class AIChatRequest(BaseModel):
    prompt: str
    type: str = "general"      # general | mentor | psychology | strategy
    context: Optional[Dict[str, Any]] = {}


# System prompts per chat type
_CHAT_SYSTEM = {
    "mentor": (
        "Kamu adalah AI Mentor trading profesional untuk platform GAS Strategy AI. "
        "Berikan review dan coaching layaknya senior trader dengan 10+ tahun pengalaman. "
        "Fokus pada: analisa entry/exit, risk management, mindset, dan perbaikan konkret. "
        "Gunakan bahasa Indonesia yang jelas dan actionable."
    ),
    "psychology": (
        "Kamu adalah AI Psychology Coach untuk trader. Bantu trader mengenali dan mengatasi "
        "bias psikologis: FOMO, revenge trade, overconfidence, fear. "
        "Berikan saran mindset yang empatik tapi tegas dalam bahasa Indonesia."
    ),
    "strategy": (
        "Kamu adalah AI Strategy Analyst untuk GAS Strategy AI. "
        "Analisa dan evaluasi strategi trading berdasarkan data yang diberikan. "
        "Fokus pada win rate, risk/reward, dan optimasi parameter. Bahasa Indonesia."
    ),
    "general": (
        "Kamu adalah AI assistant untuk platform trading GAS Strategy AI. "
        "Bantu trader dengan pertanyaan seputar forex, gold, analisa teknikal, "
        "fundamental, dan manajemen risiko. Bahasa Indonesia, singkat dan jelas."
    ),
}


@app.post("/v1/ai/chat")
async def ai_chat(req: AIChatRequest):
    """
    General AI chat endpoint — used by Mentor Mode, AI Bloomberg Terminal, and other chat features.
    Routes to DeepSeek via OpenRouter.
    """
    system = _CHAT_SYSTEM.get(req.type, _CHAT_SYSTEM["general"])

    # Enrich prompt with context if provided
    context_text = ""
    if req.context:
        ctx_pairs = [f"{k}: {v}" for k, v in req.context.items() if v]
        if ctx_pairs:
            context_text = "\n\nKonteks:\n" + "\n".join(ctx_pairs)

    full_prompt = req.prompt + context_text

    response_text = await ai.ask_ai(system, full_prompt, max_tokens=800)

    return {
        "response": response_text,
        "type": req.type,
        "source": "deepseek-openrouter",
    }


@app.get("/v1/cache/status")
async def cache_status():
    """Check what's currently cached."""
    from src.cache import get_cached_sentiment, get_cached_fundamental, get_cached_calendar, get_cached_snapshot

    briefing_daily = await get_cached_briefing("daily")
    briefing_weekly = await get_cached_briefing("weekly")
    sentiment = await get_cached_sentiment()
    fundamental = await get_cached_fundamental()
    calendar = await get_cached_calendar()
    snapshot = await get_cached_snapshot()

    return {
        "cache_status": {
            "briefing_daily": {
                "cached": briefing_daily is not None,
                "date": briefing_daily.get("date") if briefing_daily else None,
                "generated_at": briefing_daily.get("generated_at") if briefing_daily else None,
            },
            "briefing_weekly": {
                "cached": briefing_weekly is not None,
                "week": briefing_weekly.get("week") if briefing_weekly else None,
            },
            "sentiment": {
                "cached": sentiment is not None,
                "fetched_at": sentiment.get("fetched_at") if sentiment else None,
            },
            "fundamental": {
                "cached": fundamental is not None,
                "fetched_at": fundamental.get("fetched_at") if fundamental else None,
            },
            "calendar": {
                "cached": calendar is not None,
                "event_count": len(calendar) if calendar else 0,
            },
            "mt5_snapshot": {
                "cached": snapshot is not None,
                "fetched_at": snapshot.get("fetched_at") if snapshot else None,
                "pairs": list(snapshot.get("pairs", {}).keys()) if snapshot else [],
            },
        }
    }


# ── Legacy Endpoint ───────────────────────────────────────────────────────────

@app.post("/v1/strategy/evaluate")
def evaluate_strategy(req: EvaluationRequest):
    try:
        return evaluate(req.strategy_name, req.data, req.context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Technical Analysis ────────────────────────────────────────────────────────

@app.post("/v1/analysis/technical")
async def technical_analysis(req: TechnicalAnalysisRequest):
    """
    Technical analysis — Indicator Engine + SMC Engine.
    pure_compute=True: skip LLM → deterministic rule-based output (faster, cheaper).
    pure_compute=False (default): adds AI narrative interpretation via LLM.
    """
    candles = await get_ohlc_smart(req.pair, req.timeframe, limit=200)
    if not candles:
        raise HTTPException(
            status_code=503,
            detail=f"No OHLC data for {req.pair}/{req.timeframe}. Check MT5 EA or Binance service.",
        )

    # Resolve effective compute level
    # Precedence: compute_level > pure_compute (backward compat)
    if req.compute_level in ("FAST", "STANDARD", "FULL"):
        effective_level = req.compute_level
    elif req.pure_compute:
        effective_level = "STANDARD"  # pure_compute=True → indicators+SMC, no LLM
    else:
        effective_level = "FULL"

    # Feature Builder: indicator + SMC
    # FAST skips SMC engine call (just indicators), STANDARD+FULL run full pipeline
    from src.indicators.technical import compute_indicators_only
    if effective_level == "FAST":
        # Indicators only — no SMC call, fastest path
        features = compute_indicators_only(req.pair, req.timeframe, candles)
    else:
        features = await _build_feature_summary(req.pair, req.timeframe, candles)

    current_price  = features.get("current_price", 0)
    recommendation = features.get("recommendation", "NEUTRAL")
    confidence     = features.get("confidence", 0)
    confluence     = features.get("confluence_score", 0)
    setup_type     = features.get("setup_type", "Unknown")
    smc            = features.get("SMC") or {}

    if effective_level in ("FAST", "STANDARD"):
        # ── Pure deterministic output — NO LLM call ────────────────────────────
        rsi_val  = features.get("RSI", {})
        rsi_v    = rsi_val.get("value", 0) if isinstance(rsi_val, dict) else 0
        ema_data = features.get("EMA", {})
        reasons  = []
        if isinstance(rsi_val, dict):
            sig = rsi_val.get("signal", "")
            if sig:
                reasons.append(f"RSI {rsi_v:.1f} → {sig}")
        macd_data = features.get("MACD", {})
        if isinstance(macd_data, dict):
            ms = macd_data.get("signal", "")
            if ms:
                reasons.append(f"MACD → {ms}")
        adx_data = features.get("ADX", {})
        if isinstance(adx_data, dict):
            av = adx_data.get("value", 0)
            if av:
                reasons.append(f"ADX {av:.1f} ({'trend kuat' if av > 25 else 'ranging'})")
        smc_bias = smc.get("bias", "")
        if smc_bias:
            reasons.append(f"SMC bias {smc_bias}")
        reason_str = " | ".join(reasons) if reasons else f"{recommendation} confluence={confluence}%"
        ai_text = (
            f"[Pure Compute] {recommendation} signal untuk {req.pair} {req.timeframe}. "
            f"Confidence: {confidence}% | Confluence: {confluence}%. "
            f"{reason_str}"
        )
        source = f"pure-compute:{effective_level.lower()}"
    else:
        # ── FULL: AI narrative interpretation via LLM ─────────────────────────
        ai_text = await ai.analyze_technical(req.pair, req.timeframe, features, current_price)
        source  = "real-data"

    return {
        "pair":             req.pair,
        "timeframe":        req.timeframe,
        "candle_count":     len(candles),
        "current_price":    current_price,
        "signals":          {k: v for k, v in features.items() if k in ["RSI", "MACD", "ADX", "BB", "EMA", "SMC"]},
        "recommendation":   recommendation,
        "confidence":       confidence,
        "confluence_score": confluence,
        "setup_type":       setup_type,
        "smc_available":    bool(smc),
        "ai_interpretation": ai_text,
        "pure_compute":     req.pure_compute,
        "compute_level":    effective_level,
        "source":           source,
    }


# ── Signal System ─────────────────────────────────────────────────────────────

@app.post("/v1/analysis/signal")
async def signal_analysis(req: SignalRequest):
    """
    Premium signal — Multi-TF Feature Builder + DXY Correlation + SMC Engine → AI.
    5-Layer: OHLCV multi-TF + Indicator Engine + SMC Structure + Macro (DXY) + News filter.
    DXY correlation: DXY↑=XAU↓ (SELL), DXY↓=XAU↑ (BUY).
    """
    style = req.style or "intraday"

    # ── Layer 1-4: Multi-TF + DXY Correlation ──────────────────────────────────
    mtf_data = await _build_mtf_features_with_dxy(req.pair, style)
    primary_features = mtf_data.get("primary_features") or {}
    current_price = primary_features.get("current_price", 0)

    # Fallback: if no primary features, try single-TF
    if not current_price:
        candles = await get_ohlc_smart(req.pair, req.timeframe, limit=200)
        if not candles:
            raise HTTPException(status_code=503, detail=f"No data for {req.pair}/{req.timeframe}")
        primary_features = await _build_feature_summary(req.pair, req.timeframe, candles)
        current_price = primary_features.get("current_price", 0)

    # ── Layer 5: Macro (DXY) context ────────────────────────────────────────────
    dxy_data = mtf_data.get("dxy", {})
    correlation_signal = mtf_data.get("correlation_signal", "NEUTRAL")
    xau_overall = mtf_data.get("xau_overall", "NEUTRAL")

    # Build DXY context string for AI prompt
    dxy_context = {
        "dxy_available": dxy_data.get("available", False),
        "dxy_overall": dxy_data.get("overall", "NEUTRAL"),
        "dxy_tfs": dxy_data.get("tfs", {}),
        "xau_overall": xau_overall,
        "correlation_signal": correlation_signal,
        "mtf_summary": {tf: v.get("trend") for tf, v in mtf_data.get("mtf", {}).items()},
        "style": style,
        "note": (
            f"DXY {'↑ BEARISH untuk XAU' if dxy_data.get('overall') == 'BULLISH' else '↓ BULLISH untuk XAU' if dxy_data.get('overall') == 'BEARISH' else 'NEUTRAL'}. "
            f"XAU trend: {xau_overall}. Konfluensi DXY: {correlation_signal}."
        ),
    }

    signal_data = await ai.analyze_signal_tiered(
        req.pair, mtf_data.get("primary_tf", req.timeframe),
        primary_features, current_price, req.model_tier,
        dxy_context=dxy_context,
        market=getattr(req, "market", "forex"),
    )

    # ── Enrich signal with SMC + MTF + DXY ─────────────────────────────────────
    signal_data["setup_type"] = primary_features.get("setup_type", "Unknown")
    signal_data["confluence_score"] = primary_features.get("confluence_score", 0)
    signal_data["style"] = style
    signal_data["correlation_signal"] = correlation_signal
    signal_data["dxy_bias"] = dxy_data.get("overall", "NEUTRAL")
    signal_data["xau_bias"] = xau_overall
    signal_data["mtf_trend"] = {tf: v.get("trend") for tf, v in mtf_data.get("mtf", {}).items()}
    signal_data["mtf_detail"] = mtf_data.get("mtf", {})

    smc = primary_features.get("SMC")
    if smc:
        signal_data["smc_bias"] = smc.get("bias", "NEUTRAL")
        signal_data["smc_score"] = smc.get("smc_score", 0)
        signal_data["kill_zone"] = smc.get("kill_zone", False)
        signal_data["amd_phase"] = smc.get("amd_phase", "")
        signal_data["smc_available"] = True
    else:
        signal_data["smc_available"] = False

    return {
        "pair": req.pair,
        "timeframe": mtf_data.get("primary_tf", req.timeframe),
        "current_price": current_price,
        **signal_data,
        "source": "real-data",
    }


# ── Sentiment Analysis ────────────────────────────────────────────────────────

@app.post("/v1/analysis/sentiment")
async def sentiment_analysis(req: SentimentRequest):
    """Real sentiment from Fear/Greed API + CFTC COT data."""
    # Fetch all sentiment data in parallel
    fear_greed, cot_gold, cot_dxy = await asyncio.gather(
        fetch_fear_greed(),
        fetch_cot_gold(),
        fetch_cot_dxy(),
    )

    ai_text = await ai.analyze_sentiment(fear_greed, cot_gold, cot_dxy, req.pair)

    return {
        "pair": req.pair,
        "fear_greed": fear_greed,
        "cot_gold": cot_gold,
        "cot_dxy": cot_dxy,
        "ai_signal": ai_text,
        "source": "real-data",
    }


# ── Fundamental Analysis ──────────────────────────────────────────────────────

@app.post("/v1/analysis/fundamental")
async def fundamental_analysis(req: TechnicalAnalysisRequest):
    """Real macro data from tedata (TradingEconomics scraper)."""
    macro_data = get_macro_data("United States")
    ai_text = await ai.analyze_fundamental(macro_data, req.pair)

    return {
        "pair": req.pair,
        "macro_data": macro_data,
        "ai_analysis": ai_text,
        "source": "real-data",
    }


# ── Economic Calendar ─────────────────────────────────────────────────────────

@app.post("/v1/analysis/calendar")
async def calendar_analysis(req: BriefingRequest):
    """Real economic calendar from ecocal library."""
    events = get_upcoming_events(currencies=None, impact="medium")  # all major currencies, high+medium

    return {
        "events": events,
        "high_impact_count": len([e for e in events if "HIGH" in str(e.get("impact", "")).upper()]),
        "source": "real-data",
    }


# ── RAG Enrichment Helpers ────────────────────────────────────────────────────

async def _fetch_rag_macro(symbol: str, query: str) -> dict:
    """Call gas-rag-macro for RAG-augmented macro analysis. Returns {} on failure."""
    try:
        from src.config import settings as _settings
        import httpx as _httpx
        payload = {"symbol": symbol, "query": query, "time_horizon": "24h",
                   "include_news": True, "include_calendar": True, "include_price_data": True}
        async with _httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(f"{_settings.RAG_MACRO_URL}/macro/analyze", json=payload)
            if resp.status_code == 200:
                return resp.json()
    except Exception as exc:
        log.warning(f"rag-macro unavailable: {exc}")
    return {}


async def _fetch_rag_technical(symbol: str, timeframe: str) -> dict:
    """Call gas-rag-technical for RAG-augmented technical analysis. Returns {} on failure."""
    try:
        from src.config import settings as _settings
        import httpx as _httpx
        payload = {"symbol": symbol, "timeframe": timeframe,
                   "query": f"Technical analysis and key levels for {symbol} {timeframe}"}
        async with _httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(f"{_settings.RAG_TECHNICAL_URL}/analyze", json=payload)
            if resp.status_code == 200:
                return resp.json()
    except Exception as exc:
        log.warning(f"rag-technical unavailable: {exc}")
    return {}


# ── Market Briefing (cache-first) ─────────────────────────────────────────────

@app.post("/v1/analysis/briefing")
async def market_briefing(req: BriefingRequest):
    """
    AI market briefing — reads from Redis cache (pre-generated at 06:30 WIB).
    If cache miss (first request of the day), generates on-demand and caches.
    """
    # 1. Try cache first
    cached = await get_cached_briefing(req.type)
    if cached:
        cached["from_cache"] = True
        cached["cache_note"] = f"Pre-generated at {cached.get('generated_at', 'unknown')}. Next auto-refresh: 06:30 WIB"
        return cached

    # 2. Cache miss — generate now (and cache for next requests)
    log.info(f"Briefing cache miss for type={req.type} — generating on-demand...")

    # Fetch macro data, calendar, fear/greed, and XAU/DXY multi-TF in parallel
    fear_greed, macro_data, mtf_xau, dxy_h4, dxy_h1 = await asyncio.gather(
        fetch_fear_greed(),
        asyncio.to_thread(get_macro_data, "United States"),
        _build_mtf_features_with_dxy("XAUUSD", "intraday"),  # H4/H1/M15/M5
        _get_dxy_candles("H4", limit=100),
        _get_dxy_candles("H1", limit=100),
    )
    calendar_events = get_upcoming_events()

    # Build DXY multi-TF summary for briefing
    dxy_briefing = mtf_xau.get("dxy", {})
    correlation_signal = mtf_xau.get("correlation_signal", "NEUTRAL")
    xau_mtf_summary = {tf: v.get("trend") for tf, v in mtf_xau.get("mtf", {}).items()}

    mtf_context = {
        "xau_mtf": xau_mtf_summary,
        "xau_overall": mtf_xau.get("xau_overall", "NEUTRAL"),
        "dxy_overall": dxy_briefing.get("overall", "NEUTRAL"),
        "dxy_tfs": dxy_briefing.get("tfs", {}),
        "correlation_signal": correlation_signal,
        "dxy_available": dxy_briefing.get("available", False),
    }

    # Fetch RAG enrichment in parallel (non-blocking — failures are silently ignored)
    rag_macro_res, rag_tech_res = await asyncio.gather(
        _fetch_rag_macro("XAUUSD", f"Macro outlook and key drivers for XAUUSD {req.type} briefing"),
        _fetch_rag_technical("XAUUSD", "H4"),
        return_exceptions=True,
    )
    if isinstance(rag_macro_res, Exception):
        rag_macro_res = {}
    if isinstance(rag_tech_res, Exception):
        rag_tech_res = {}

    ai_structured = await ai.analyze_briefing(macro_data, calendar_events, fear_greed, req.type, mtf_context=mtf_context)

    # Blend RAG insights into ai_structured (non-destructive enrichment)
    if rag_macro_res.get("summary"):
        ai_structured.setdefault("rag_macro_summary", rag_macro_res["summary"])
        ai_structured.setdefault("rag_macro_sentiment", rag_macro_res.get("sentiment", "neutral"))
        ai_structured.setdefault("rag_key_factors", rag_macro_res.get("key_factors", []))
    if rag_tech_res.get("analysis") or rag_tech_res.get("summary"):
        ai_structured.setdefault("rag_technical_summary", rag_tech_res.get("analysis") or rag_tech_res.get("summary", ""))
        ai_structured.setdefault("rag_key_levels", rag_tech_res.get("key_levels", []))

    from datetime import datetime, timezone, timedelta
    wib = timezone(timedelta(hours=7))
    now_wib = datetime.now(wib)

    # Indonesian month names
    MONTHS_ID = ["Januari","Februari","Maret","April","Mei","Juni",
                 "Juli","Agustus","September","Oktober","November","Desember"]
    DAYS_ID = ["Senin","Selasa","Rabu","Kamis","Jumat","Sabtu","Minggu"]
    day_name = DAYS_ID[now_wib.weekday()]
    month_name = MONTHS_ID[now_wib.month - 1]
    date_str = f"{day_name}, {now_wib.day} {month_name} {now_wib.year}"
    time_str = now_wib.strftime("%H:%M WIB")
    generated_at = now_wib.isoformat()

    result = {
        "type": req.type,
        "date": date_str,
        "time": time_str,
        "generated_at": generated_at,
        "fear_greed": fear_greed,
        "macro_summary": ai_structured.get("macro_summary", str(macro_data)[:200]),
        "headline": ai_structured.get("headline", f"Market {req.type.title()} Briefing — {date_str}"),
        "market_bias": ai_structured.get("market_bias", "neutral"),
        "smart_money_view": ai_structured.get("smart_money_view", ""),
        "trading_advice": ai_structured.get("trading_advice", ""),
        "pairs_outlook": ai_structured.get("pairs_outlook", []),
        "key_events": ai_structured.get("key_events", calendar_events[:5]),
        "xau_plan": ai_structured.get("xau_plan", {}),
        # DXY correlation enrichment
        "dxy_bias": dxy_briefing.get("overall", "NEUTRAL"),
        "xau_mtf": xau_mtf_summary,
        "xau_overall": mtf_xau.get("xau_overall", "NEUTRAL"),
        "correlation_signal": correlation_signal,
        "dxy_available": dxy_briefing.get("available", False),
        "ai_briefing": ai_structured,
        # RAG-enriched insights (from gas-rag-macro + gas-rag-technical)
        "rag_macro_summary": ai_structured.get("rag_macro_summary", ""),
        "rag_macro_sentiment": ai_structured.get("rag_macro_sentiment", "neutral"),
        "rag_key_factors": ai_structured.get("rag_key_factors", []),
        "rag_technical_summary": ai_structured.get("rag_technical_summary", ""),
        "rag_key_levels": ai_structured.get("rag_key_levels", []),
        "from_cache": False,
        "source": "real-data",
    }

    await set_cached_briefing(result, req.type)
    return result


# ── Hybrid Analysis ───────────────────────────────────────────────────────────

@app.post("/v1/analysis/hybrid")
async def hybrid_analysis(req: HybridAnalysisRequest):
    """Real hybrid: TA + SMC + FA sentiment + COT data + DXY correlation confluence score."""
    # Fetch data in parallel — OHLC + external data + DXY
    candles, fear_greed, cot_gold, dxy_bias = await asyncio.gather(
        get_ohlc_smart(req.pair, req.timeframe, limit=200),
        fetch_fear_greed(),
        fetch_cot_gold(),
        _compute_dxy_bias(["H4", "H1"]),
    )

    if not candles:
        raise HTTPException(status_code=503, detail=f"No data for {req.pair}/{req.timeframe}")

    # Feature Builder: indicator + SMC combined
    features = await _build_feature_summary(req.pair, req.timeframe, candles)
    current_price = features.get("current_price", 0)
    smc_feat = features.get("SMC")

    # TA score
    ta_conf = features.get("confidence", 50)
    ta_rec  = features.get("recommendation", "NEUTRAL")
    ta_score = ta_conf if ta_rec == "BUY" else (100 - ta_conf if ta_rec == "SELL" else 50)

    # SMC score (from Feature Builder)
    smc_score = smc_feat.get("smc_score", 0) if smc_feat else None

    # Sentiment score from Fear/Greed
    fg_val = fear_greed.get("index") or 50
    sentiment_score = int(fg_val)

    # FA score from COT
    cot_nc  = cot_gold.get("non_commercial", {})
    cot_net = cot_nc.get("net", 0)
    fa_score = min(100, max(0, 50 + int(cot_net / 1000))) if cot_net else 50

    # DXY correlation score (5th layer)
    dxy_overall = dxy_bias.get("overall", "NEUTRAL")
    corr_signal = _apply_dxy_correlation(
        "BULLISH" if ta_rec == "BUY" else ("BEARISH" if ta_rec == "SELL" else "NEUTRAL"),
        dxy_overall
    )
    dxy_score = 75 if "CONFIRMED" in corr_signal else (50 if "CAUTION" in corr_signal else 25)

    # Confluence: 5-way blend (TA + FA + Sentiment + SMC + DXY)
    scores = [ta_score, sentiment_score, fa_score, dxy_score]
    if smc_score is not None:
        scores.append(smc_score)
    confluence = sum(scores) // len(scores)

    overall = "BUY" if confluence > 60 else "SELL" if confluence < 40 else "NEUTRAL"

    ai_text = await ai.analyze_hybrid(ta_score, fa_score, sentiment_score, features, req.pair, current_price, dxy_data={"overall": dxy_overall, "score": dxy_score, "correlation": corr_signal})

    signals = [
        {"source": "Technical (Indicator Engine)", "signal": ta_rec, "detail": f"Confidence {ta_conf}%"},
        {"source": "Sentiment (Fear/Greed)", "signal": "BULLISH" if fg_val > 50 else "BEARISH", "detail": f"Fear/Greed: {fg_val} ({fear_greed.get('label', '')})"},
        {"source": "Fundamental (COT)", "signal": cot_nc.get("bias", "UNKNOWN"), "detail": f"Net position: {cot_net}"},
        {"source": "DXY Correlation", "signal": corr_signal, "detail": f"DXY {dxy_overall} → XAU {'inverse' if dxy_bias.get('available') else 'no data'} | Score {dxy_score}/100"},
    ]
    if smc_feat:
        signals.append({
            "source": "SMC Engine",
            "signal": smc_feat.get("smc_action", "WAIT"),
            "detail": f"Bias: {smc_feat.get('bias','N/A')} | Setup: {features.get('setup_type','Unknown')} | AMD: {smc_feat.get('amd_phase','?')}",
        })

    result = {
        "pair": req.pair,
        "timeframe": req.timeframe,
        "current_price": current_price,
        "confluence_score": confluence,
        "ta_score": ta_score,
        "fa_score": fa_score,
        "sentiment_score": sentiment_score,
        "dxy_score": dxy_score,
        "dxy_bias": dxy_overall,
        "correlation_signal": corr_signal,
        "recommendation": overall,
        "signals": signals,
        "ai_decision": ai_text,
        "setup_type": features.get("setup_type", "Unknown"),
        "smc_available": smc_feat is not None,
        "source": "real-data",
    }
    if smc_score is not None:
        result["smc_score"] = smc_score
    if smc_feat:
        result["smc_data"] = smc_feat

    return result


# ── Risk Manager ──────────────────────────────────────────────────────────────

@app.post("/v1/analysis/risk")
async def risk_manager(req: RiskRequest):
    """Risk calculation using real MT5 account data from Redis."""
    account = None
    if req.user_id:
        account = await get_account(req.user_id)

    balance = account["balance"] if account else (req.balance or 10000.0)
    equity = account["equity"] if account else balance
    risk_pct = req.risk_pct or 1.0
    risk_amount = balance * (risk_pct / 100)
    sl_pips = req.sl_pips or 150
    lot_size = round(risk_amount / (sl_pips * 10), 2)

    # Calculate portfolio heat from real positions
    positions = []
    if req.user_id:
        positions = await get_positions(req.user_id)

    floating_dd = ((balance - equity) / balance * 100) if balance > 0 and account else 0
    portfolio_heat = abs(floating_dd)

    alert = None
    if risk_pct > 2:
        alert = f"Risk {risk_pct}% melebihi batas aman 2%."
    if portfolio_heat > 5:
        alert = f"Portfolio heat {portfolio_heat:.1f}% — berbahaya! Kurangi posisi."

    return {
        "balance": round(balance, 2),
        "equity": round(equity, 2),
        "risk_pct": risk_pct,
        "risk_amount_usd": round(risk_amount, 2),
        "recommended_lot": max(0.01, lot_size),
        "portfolio_heat": round(portfolio_heat, 2),
        "open_positions": len(positions),
        "alert": alert,
        "ai_advice": f"Balance real ${balance:,.0f} | Risk {risk_pct}% = ${risk_amount:.0f} | Lot optimal {max(0.01, lot_size):.2f} | Heat {portfolio_heat:.1f}%",
        "source": "real-data" if account else "calculated",
        "data_from": "mt5_redis" if account else "manual_input",
    }


# ── Drawdown Recovery ─────────────────────────────────────────────────────────

@app.post("/v1/analysis/drawdown")
async def drawdown_recovery(req: DrawdownRequest):
    """Real drawdown from MT5 account data in Redis."""
    account = None
    if req.user_id:
        account = await get_account(req.user_id)

    if account:
        balance = account["balance"]
        equity = account["equity"]
        floating_pnl = account.get("floating_pnl", 0)
        daily_pnl = account.get("daily_pnl", 0)
        dd_pct = ((balance - equity) / balance * 100) if balance > 0 else 0
    else:
        dd_pct = 0
        balance = 0
        equity = 0
        floating_pnl = 0
        daily_pnl = 0

    dd_mode = dd_pct > 5

    recovery_plan = []
    if dd_pct > 15:
        recovery_plan = ["STOP TRADING SEKARANG — DD melebihi 15%", "Review semua strategi", "Konsultasi mentor"]
    elif dd_pct > 10:
        recovery_plan = ["Kurangi lot 75%", "Hanya setup A+ dengan RR 1:4+", "Maksimal 1 trade per hari", "Review jurnal 7 hari terakhir"]
    elif dd_pct > 5:
        recovery_plan = ["Kurangi lot 50% sampai DD < 5%", "Hindari open posisi baru dalam 6 jam", "Fokus setup dengan 3+ konfirmasi", "Set SL lebih ketat"]
    else:
        recovery_plan = ["DD dalam batas normal", "Lanjutkan strategi normal", "Monitor equity setiap 2 jam"]

    return {
        "balance": round(balance, 2),
        "equity": round(equity, 2),
        "floating_pnl": round(floating_pnl, 2),
        "daily_pnl": round(daily_pnl, 2),
        "current_dd_pct": round(abs(dd_pct), 2),
        "dd_mode": dd_mode,
        "risk_reduction": "75%" if dd_pct > 10 else "50%" if dd_pct > 5 else "0%",
        "recovery_plan": recovery_plan,
        "revenge_trade_alert": dd_pct > 5 and daily_pnl < 0,
        "ai_message": f"DD real: {abs(dd_pct):.1f}%. {'Mode recovery aktif.' if dd_mode else 'Dalam batas aman.'} {recovery_plan[0]}",
        "source": "real-data" if account else "no_mt5_data",
    }


# ── Psychology ────────────────────────────────────────────────────────────────

@app.post("/v1/analysis/psychology")
async def psychology_analysis(req: PsychologyRequest):
    """Psychology coach with real AI analysis."""
    emotion_scores = {"calm": 85, "nervous": 55, "fomo": 30, "revenge": 15, "greedy": 40, "confident": 75}
    base_score = emotion_scores.get(req.emotion.lower(), 60)
    risk_penalties = {"fomo": 20, "revenge": 25, "oversize": 15, "noplan": 20, "greedy": 10}
    penalty = sum(risk_penalties.get(r, 5) for r in req.risks)
    final_score = max(5, base_score - penalty)
    safe = final_score >= 50

    ai_text = await ai.analyze_psychology(req.emotion, req.risks, req.recent_pnl)

    return {
        "emotion": req.emotion,
        "emotion_score": final_score,
        "safe_to_trade": safe,
        "risks_detected": req.risks,
        "ai_coaching": ai_text,
        "source": "real-ai",
    }


# ── Scanner ───────────────────────────────────────────────────────────────────

@app.post("/v1/analysis/scanner")
async def scanner(req: ScannerRequest):
    """
    Premium multi-symbol scanner — Kimi 2.5 AI per pair.
    Returns entry/SL/TP1/TP2/TP3, probability, trigger, reasoning per pair.
    """
    default_pairs = [
        # Forex & Commodity (MT5)
        "XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "XAGUSD", "AUDUSD", "GBPJPY",
        "USDCAD", "NZDUSD", "USDCHF", "US30", "NAS100",
        # Crypto (Binance)
        "BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "BNB/USDT",
        "ADA/USDT", "DOGE/USDT", "AVAX/USDT", "LINK/USDT",
    ]
    pairs_to_scan = req.pairs if req.pairs else default_pairs

    # Pre-fetch DXY bias once for all pairs (avoid N × DXY fetches)
    scanner_dxy = await _compute_dxy_bias(["H4", "H1"])

    # Limit concurrent AI calls to prevent OpenRouter rate-limit and timeout
    sem = asyncio.Semaphore(5)

    async def scan_pair(symbol: str):
        try:
            candles = await get_ohlc_smart(symbol, req.timeframe, limit=100)
            if not candles:
                return None
            ind = compute_indicators(candles)
            price = ind.get("current_price", 0)
            conf = ind.get("confidence", 0)

            # Only call AI for pairs that pass basic technical threshold
            if conf < req.min_confluence:
                return None

            # Inject DXY context for XAU pairs
            if symbol in ("XAUUSD", "XAGUSD"):
                xau_trend = _trend_from_indicators(ind)
                corr = _apply_dxy_correlation(xau_trend, scanner_dxy.get("overall", "NEUTRAL"))
                ind["_dxy_correlation"] = corr
                ind["_dxy_bias"] = scanner_dxy.get("overall", "NEUTRAL")

            # Call tiered AI with semaphore to limit concurrent requests
            async with sem:
                sig_data = await asyncio.wait_for(
                    ai.analyze_pair_scanner_tiered(symbol, req.timeframe, ind, price, req.model_tier),
                    timeout=25.0,
                )
            sig_data["confluence_score"] = conf
            return sig_data
        except asyncio.TimeoutError:
            return None
        except Exception:
            return None

    scan_tasks = [scan_pair(p) for p in pairs_to_scan]
    results_raw = await asyncio.gather(*scan_tasks)
    results = [r for r in results_raw if r is not None]

    # Sort: actionable signals first, then by probability
    def sort_key(r):
        actionable = 1 if r.get("signal") in ("BUY", "SELL") else 0
        return (actionable, r.get("probability", 0))

    results.sort(key=sort_key, reverse=True)
    for i, r in enumerate(results):
        r["rank"] = i + 1

    ai_summary = await ai.analyze_scanner(results[:5]) if results else "Tidak ada pair yang memenuhi threshold."

    return {
        "scanned": len(pairs_to_scan),
        "qualified": len(results),
        "min_confluence": req.min_confluence,
        "results": results,
        "top_pick": results[0] if results else None,
        "ai_summary": ai_summary,
        "model": "kimi-2.5",
        "source": "real-data",
    }


# ── Correlation Tracker ────────────────────────────────────────────────────────

@app.post("/v1/analysis/correlation")
async def correlation_analysis(req: CorrelationRequest):
    """Real Pearson correlation matrix across multiple pairs using live OHLC from MT5/Binance."""
    import numpy as np

    corr_pairs = ["XAUUSD", "EURUSD", "USDJPY", "GBPUSD", "XAGUSD"]
    # Ensure requested pair is included
    if req.pair not in corr_pairs:
        corr_pairs.insert(0, req.pair)
    # Add DXY if available — DXY vs XAU is the key correlation
    for dxy_sym in DXY_SYMBOLS:
        try:
            test = await get_ohlc(dxy_sym, req.timeframe, 5)
            if test:
                corr_pairs.insert(0, dxy_sym)
                break
        except Exception:
            pass

    async def fetch_closes(symbol: str):
        try:
            candles = await get_ohlc_smart(symbol, req.timeframe, limit=100)
            if candles and len(candles) >= 20:
                return symbol, [c["close"] for c in candles]
        except Exception:
            pass
        return symbol, None

    raw = await asyncio.gather(*[fetch_closes(p) for p in corr_pairs])
    price_series = {sym: closes for sym, closes in raw if closes}

    if len(price_series) < 2:
        raise HTTPException(status_code=503, detail="Tidak cukup data pair untuk korelasi. Cek koneksi MT5 EA.")

    min_len = min(len(v) for v in price_series.values())
    live_prices = {sym: round(prices[-1], 5) for sym, prices in price_series.items()}

    # Compute Pearson correlation matrix
    correlation_matrix: Dict[str, Dict[str, float]] = {}
    pairs_list = list(price_series.keys())
    for sym in pairs_list:
        correlation_matrix[sym] = {}
        x = np.array(price_series[sym][-min_len:])
        for sym2 in pairs_list:
            y = np.array(price_series[sym2][-min_len:])
            if len(x) > 1:
                corr = float(np.corrcoef(x, y)[0, 1])
                correlation_matrix[sym][sym2] = round(corr, 3)

    ai_text = await ai.analyze_correlation(correlation_matrix, req.pair, live_prices)

    # DXY-XAU correlation highlight
    dxy_xau_corr = None
    dxy_sym_used = next((s for s in DXY_SYMBOLS if s in correlation_matrix), None)
    if dxy_sym_used and "XAUUSD" in correlation_matrix.get(dxy_sym_used, {}):
        dxy_xau_corr = correlation_matrix[dxy_sym_used]["XAUUSD"]

    return {
        "pair": req.pair,
        "timeframe": req.timeframe,
        "candles_used": min_len,
        "live_prices": live_prices,
        "correlation_matrix": correlation_matrix,
        "pairs_analyzed": pairs_list,
        "dxy_xau_correlation": dxy_xau_corr,
        "dxy_note": (
            f"DXY↑=XAU↓ (inverse). Korelasi saat ini: {dxy_xau_corr:.3f}. "
            f"{'Konfirmasi inverse correlation normal.' if dxy_xau_corr and dxy_xau_corr < -0.3 else 'Anomali — korelasi DXY-XAU melemah.'}"
        ) if dxy_xau_corr is not None else "DXY tidak tersedia di broker ini.",
        "interpretation": {
            "strong_positive": "> +0.70 = bergerak searah",
            "strong_negative": "< -0.70 = bergerak berlawanan (hedge natural)",
            "neutral": "-0.30 to +0.30 = tidak berkorelasi",
        },
        "ai_interpretation": ai_text,
        "source": "real-data",
    }


# ── Backtesting Engine ─────────────────────────────────────────────────────────

@app.post("/v1/analysis/backtesting")
async def backtesting_engine(req: BacktestRequest):
    """Walk-forward backtesting using real OHLC history from MT5/Binance."""
    candles = await get_ohlc_smart(req.pair, req.timeframe, limit=req.lookback)

    if not candles or len(candles) < 50:
        raise HTTPException(status_code=503, detail=f"Data tidak cukup untuk backtesting {req.pair}/{req.timeframe}. Butuh minimal 50 candle dari MT5 EA.")

    trades = []
    i = 20  # warmup period

    while i < len(candles) - 5:
        window = candles[:i + 1]
        ind = compute_indicators(window)
        rec = ind.get("recommendation", "NEUTRAL")
        conf = ind.get("confidence", 0)

        if rec in ("BUY", "SELL") and conf >= 60:
            entry_price = candles[i]["close"]
            # ATR proxy: average true range of last 5 bars
            atr = sum(
                abs(candles[j]["high"] - candles[j]["low"])
                for j in range(max(0, i - 4), i + 1)
            ) / 5
            sl_dist = max(atr * 1.5, entry_price * 0.001)  # at least 0.1% of price
            tp_dist = sl_dist * req.rr_ratio

            hit_tp = hit_sl = False
            for j in range(i + 1, min(i + 11, len(candles))):
                if rec == "BUY":
                    if candles[j]["high"] >= entry_price + tp_dist:
                        hit_tp = True; break
                    if candles[j]["low"] <= entry_price - sl_dist:
                        hit_sl = True; break
                else:  # SELL
                    if candles[j]["low"] <= entry_price - tp_dist:
                        hit_tp = True; break
                    if candles[j]["high"] >= entry_price + sl_dist:
                        hit_sl = True; break

            result = "WIN" if hit_tp else ("LOSS" if hit_sl else "PENDING")
            pnl_pct = (tp_dist / entry_price * 100) if hit_tp else ((-sl_dist / entry_price * 100) if hit_sl else 0)

            trades.append({
                "bar": i,
                "signal": rec,
                "confidence": conf,
                "entry": round(entry_price, 5),
                "sl": round(entry_price - sl_dist if rec == "BUY" else entry_price + sl_dist, 5),
                "tp": round(entry_price + tp_dist if rec == "BUY" else entry_price - tp_dist, 5),
                "result": result,
                "pnl_pct": round(pnl_pct, 3),
            })
            i += 5  # skip bars after entry to avoid double-counting
        else:
            i += 1

    if not trades:
        return {
            "pair": req.pair, "timeframe": req.timeframe,
            "lookback_candles": len(candles), "total_trades": 0,
            "message": "Tidak ada sinyal yang memenuhi threshold (confidence >= 60%) dalam data historis.",
            "source": "real-data",
        }

    wins = [t for t in trades if t["result"] == "WIN"]
    losses = [t for t in trades if t["result"] == "LOSS"]
    gross_profit = sum(t["pnl_pct"] for t in wins)
    gross_loss = abs(sum(t["pnl_pct"] for t in losses)) or 0.001
    profit_factor = round(gross_profit / gross_loss, 2)
    win_rate = round(len(wins) / len(trades) * 100, 1)
    total_return = round(sum(t["pnl_pct"] for t in trades), 2)

    # Max drawdown calculation
    cumulative = peak = max_dd = 0.0
    for t in trades:
        cumulative += t["pnl_pct"]
        peak = max(peak, cumulative)
        max_dd = max(max_dd, peak - cumulative)

    stats = {
        "total_trades": len(trades),
        "wins": len(wins),
        "losses": len(losses),
        "win_rate_pct": win_rate,
        "profit_factor": profit_factor,
        "total_return_pct": total_return,
        "max_drawdown_pct": round(max_dd, 2),
        "avg_win_pct": round(gross_profit / len(wins), 3) if wins else 0,
        "avg_loss_pct": round(-gross_loss / len(losses), 3) if losses else 0,
        "rr_ratio": req.rr_ratio,
    }

    ai_text = await ai.analyze_backtest(req.pair, req.timeframe, stats)

    return {
        "pair": req.pair,
        "timeframe": req.timeframe,
        "lookback_candles": len(candles),
        **stats,
        "ai_analysis": ai_text,
        "recent_trades": trades[-10:],
        "source": "real-data",
    }


# ── Trade Journal ──────────────────────────────────────────────────────────────

@app.post("/v1/analysis/journal")
async def journal_analysis(req: JournalRequest):
    """AI journal analysis from real MT5 account data in Redis."""
    account = None
    positions = []

    if req.user_id:
        account = await get_account(req.user_id)
        positions = await get_positions(req.user_id)

    if not account:
        raise HTTPException(
            status_code=503,
            detail="Tidak ada data MT5. Pastikan EA mengirim account heartbeat ke /api/v1/account-heartbeat."
        )

    journal_data = {
        "account": account,
        "open_positions": positions,
        "position_count": len(positions),
    }

    ai_text = await ai.analyze_journal(journal_data)

    return {
        "account_summary": {
            "balance": account.get("balance"),
            "equity": account.get("equity"),
            "floating_pnl": account.get("floating_pnl", 0),
            "margin": account.get("margin", 0),
            "margin_level": account.get("margin_level", 0),
        },
        "open_positions": positions,
        "position_count": len(positions),
        "ai_analysis": ai_text,
        "data_source": "mt5_redis_real",
        "source": "real-data",
    }


# ── Mentor Mode ────────────────────────────────────────────────────────────────

@app.post("/v1/analysis/mentor")
async def mentor_mode(req: MentorRequest):
    """AI Mentor Mode — senior trader review of current setup."""
    candles = await get_ohlc_smart(req.pair, req.timeframe, limit=200)

    if not candles:
        raise HTTPException(status_code=503, detail=f"No data for {req.pair}/{req.timeframe}. Check MT5 EA or Binance.")

    indicators = compute_indicators(candles)
    current_price = indicators.get("current_price", 0)

    account = None
    if req.user_id:
        account = await get_account(req.user_id)

    ai_text = await ai.analyze_mentor(
        req.pair, req.timeframe, indicators, current_price, account or {}, req.question or ""
    )

    return {
        "pair": req.pair,
        "timeframe": req.timeframe,
        "current_price": current_price,
        "technical_context": {
            "recommendation": indicators.get("recommendation", "NEUTRAL"),
            "confidence": indicators.get("confidence", 0),
            "rsi": indicators.get("RSI", {}).get("value"),
            "macd_signal": indicators.get("MACD", {}).get("signal"),
            "ema_signal": indicators.get("EMA", {}).get("signal"),
            "adx_strength": indicators.get("ADX", {}).get("strength"),
        },
        "mentor_review": ai_text,
        "account_linked": account is not None,
        "source": "real-data",
    }


# ── Smart Alert ────────────────────────────────────────────────────────────────

@app.post("/v1/analysis/alert")
async def create_alert(req: AlertRequest):
    """Create smart alert with real price validation."""
    from datetime import datetime, timezone
    import redis.asyncio as aioredis
    import json as _json

    # Get current price to validate alert level
    current_price = None
    try:
        candles = await get_ohlc_smart(req.pair, "M15", limit=5)
        if candles:
            current_price = candles[-1]["close"]
    except Exception:
        pass

    alert_id = f"alert:{req.user_id}:{req.pair}:{req.condition}:{int(datetime.now(timezone.utc).timestamp())}"
    alert_config = {
        "id": alert_id,
        "pair": req.pair,
        "condition": req.condition,
        "value": req.value,
        "current_price": current_price,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "active",
        "user_id": req.user_id,
    }

    # Warn if alert level doesn't make sense
    warning = None
    if current_price and req.value:
        if req.condition == "price_above" and req.value <= current_price:
            warning = f"Harga target {req.value} sudah di bawah harga saat ini {current_price:.5f}"
        elif req.condition == "price_below" and req.value >= current_price:
            warning = f"Harga target {req.value} sudah di atas harga saat ini {current_price:.5f}"

    # Store alert in Redis (TTL 24 hours)
    try:
        r = aioredis.from_url("redis://redis:6379/0", decode_responses=True)
        await r.setex(alert_id, 86400, _json.dumps(alert_config))
        await r.aclose()
        stored = True
    except Exception:
        stored = False

    return {
        "alert_created": True,
        "alert_id": alert_id,
        "config": alert_config,
        "stored_in_redis": stored,
        "warning": warning,
        "note": "Alert aktif selama 24 jam. Cek status via terminal.",
        "source": "real-data",
    }


# ── SMC Analysis ───────────────────────────────────────────────────────────────

@app.post("/v1/analysis/smc")
async def smc_analysis(req: SMCRequest):
    """
    Full SMC (Smart Money Concept) analysis for any pair.
    Supports: Forex (XAUUSD, EURUSD, GBPUSD...), Crypto (BTC/USDT, ETH/USDT...),
              Commodity (XAGUSD, US30, NAS100...).
    Data auto-routed: Binance for crypto, MT5 Redis for forex/commodity.

    Returns: Market Structure (BOS/CHoCH), Order Blocks, FVGs,
             Liquidity Pools & Sweeps, OTE zone, Kill Zone, AMD phase,
             Confluence Score, and AI interpretation.
    """
    smc_result = await run_smc_analysis(
        symbol=req.pair,
        timeframe=req.timeframe,
        trading_style=req.trading_style,
        limit=200,
    )

    if not smc_result:
        raise HTTPException(
            status_code=503,
            detail=f"SMC analysis unavailable for {req.pair}/{req.timeframe}. "
                   f"Check MT5 EA connection (forex) or gas-binance-service (crypto)."
        )

    # AI interpretation
    ai_text = await ai.analyze_smc(req.pair, req.timeframe, smc_result)

    return {
        **smc_result,
        "ai_interpretation": ai_text,
        "source": "real-data",
    }


@app.post("/v1/analysis/smc/scanner")
async def smc_scanner(req: SMCScannerRequest):
    """
    SMC multi-pair scanner — runs full SMC analysis across Binance + Forex pairs
    and returns ranked results by confluence score.
    Only pairs with actionable BUY/SELL signals and score >= min_confluence are returned.
    """
    default_pairs = [
        # Forex & Commodity (MT5 Redis)
        "XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "XAGUSD",
        "AUDUSD", "GBPJPY", "USDCAD", "NZDUSD", "USDCHF",
        "US30", "NAS100", "SPX500",
        # Crypto Spot (Binance)
        "BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "BNB/USDT",
        "ADA/USDT", "DOGE/USDT", "AVAX/USDT", "LINK/USDT", "MATIC/USDT",
        "INJ/USDT", "ARB/USDT", "OP/USDT", "APT/USDT", "SUI/USDT",
        "NEAR/USDT", "DOT/USDT", "ATOM/USDT", "UNI/USDT", "LTC/USDT",
    ]
    pairs_to_scan = req.pairs if req.pairs else default_pairs

    results = await run_smc_scanner(
        pairs=pairs_to_scan,
        timeframe=req.timeframe,
        trading_style=req.trading_style,
        min_confluence=req.min_confluence,
    )

    ai_text = await ai.analyze_scanner(results[:5]) if results else "Tidak ada setup SMC yang memenuhi threshold."

    return {
        "scanned":        len(pairs_to_scan),
        "qualified":      len(results),
        "min_confluence": req.min_confluence,
        "timeframe":      req.timeframe,
        "results":        results,
        "top_pick":       results[0] if results else None,
        "ai_summary":     ai_text,
        "source":         "real-smc",
    }


# ── AI Agent Endpoint ──────────────────────────────────────────────────────────

@app.post("/v1/analysis/agent")
async def agent_analysis(req: AgentRequest):
    """
    AI Agent trading signal — Feature Builder (Indicator Engine + SMC) → AI interpretation.
    Returns structured signal: BUY | SELL | NO TRADE with entry/SL/TP, confidence,
    reasoning, and model used. Respects min_confidence threshold.
    """
    candles = await get_ohlc_smart(req.pair, req.timeframe, limit=200)
    if not candles:
        raise HTTPException(
            status_code=503,
            detail=f"No OHLC data for {req.pair}/{req.timeframe}. Check MT5 EA or Binance service."
        )

    # Feature Builder: indicator + SMC combined
    features = await _build_feature_summary(req.pair, req.timeframe, candles)
    current_price = features.get("current_price", 0)
    confidence = features.get("confluence_score", features.get("confidence", 50))
    recommendation = features.get("recommendation", "NEUTRAL")
    smc_feat = features.get("SMC")

    # Determine signal vs threshold
    if confidence >= req.min_confidence and recommendation in ("BUY", "SELL"):
        signal = recommendation
    else:
        signal = "NO TRADE"

    # Compute SL/TP from ATR proxy if signal is actionable
    sl = None
    tp = None
    tp2 = None
    tp3 = None
    if signal in ("BUY", "SELL") and current_price:
        # ATR proxy: average of last 10 candle ranges
        recent = candles[-10:]
        atr = sum(abs(c["high"] - c["low"]) for c in recent) / len(recent)
        sl_dist = max(atr * 1.5, current_price * 0.001)
        tp_dist1 = sl_dist * 1.5
        tp_dist2 = sl_dist * 2.5
        tp_dist3 = sl_dist * 3.5

        # Use SMC SL/TP if available and more precise
        if smc_feat and smc_feat.get("smc_sl") and smc_feat.get("smc_tp"):
            sl = smc_feat["smc_sl"]
            tp = smc_feat["smc_tp"]
            tp2 = round(current_price + (tp_dist2 if signal == "BUY" else -tp_dist2), 5)
            tp3 = round(current_price + (tp_dist3 if signal == "BUY" else -tp_dist3), 5)
        else:
            if signal == "BUY":
                sl  = round(current_price - sl_dist, 5)
                tp  = round(current_price + tp_dist1, 5)
                tp2 = round(current_price + tp_dist2, 5)
                tp3 = round(current_price + tp_dist3, 5)
            else:  # SELL
                sl  = round(current_price + sl_dist, 5)
                tp  = round(current_price - tp_dist1, 5)
                tp2 = round(current_price - tp_dist2, 5)
                tp3 = round(current_price - tp_dist3, 5)

    # AI reasoning via style-aware prompt
    style_context = {
        "scalping":  "Strategi scalping — fokus M1-M15, RR minimal 1:1.5, cepat eksekusi.",
        "intraday":  "Strategi intraday — fokus M15-H1, RR minimal 1:2, close sebelum NY close.",
        "swing":     "Strategi swing — fokus H4-D1, RR minimal 1:3, hold 1-5 hari.",
    }.get(req.style, "Strategi trading standar.")

    reasoning_prompt = (
        f"Pair: {req.pair} | TF: {req.timeframe} | Harga: {current_price} | "
        f"Signal: {signal} | Confidence: {confidence}% | "
        f"Rekomendasi TA: {recommendation} | Setup: {features.get('setup_type', 'Unknown')} | "
        f"{style_context} | "
        f"RSI: {features.get('RSI', {}).get('value', 'N/A')} | "
        f"MACD: {features.get('MACD', {}).get('signal', 'N/A')} | "
        f"ADX: {features.get('ADX', {}).get('value', 'N/A')} | "
        f"SMC bias: {smc_feat.get('bias', 'N/A') if smc_feat else 'N/A'} | "
        f"Kill zone: {smc_feat.get('kill_zone', False) if smc_feat else False}. "
        f"Berikan reasoning singkat 2-3 kalimat mengapa {'eksekusi signal ini' if signal != 'NO TRADE' else 'tidak ada setup valid saat ini'}."
    )

    system_prompt = (
        "Kamu adalah AI Trading Agent untuk GAS Strategy AI. "
        "Berikan reasoning trading yang singkat, tegas, dan actionable dalam bahasa Indonesia. "
        "Fokus pada konfluensi indikator, momentum, dan konteks market structure."
    )

    try:
        reasoning = await ai.ask_ai(system_prompt, reasoning_prompt, max_tokens=250)
    except Exception:
        reasoning = (
            f"Signal {signal} pada {req.pair} {req.timeframe} dengan confidence {confidence}%. "
            f"Setup: {features.get('setup_type', 'Unknown')}. "
            f"{'Entry valid — konfluensi indikator mendukung.' if signal != 'NO TRADE' else 'Belum ada setup yang memenuhi threshold confidence.'}"
        )

    return {
        "pair": req.pair,
        "timeframe": req.timeframe,
        "style": req.style,
        "model_used": req.model,
        "signal": signal,
        "confidence": confidence,
        "min_confidence": req.min_confidence,
        "current_price": current_price,
        "entry": current_price if signal in ("BUY", "SELL") else None,
        "sl": sl,
        "tp": tp,
        "tp2": tp2,
        "tp3": tp3,
        "setup_type": features.get("setup_type", "Unknown"),
        "recommendation": recommendation,
        "confluence_score": features.get("confluence_score", 0),
        "smc_available": smc_feat is not None,
        "smc_bias": smc_feat.get("bias", "NEUTRAL") if smc_feat else None,
        "kill_zone": smc_feat.get("kill_zone", False) if smc_feat else False,
        "amd_phase": smc_feat.get("amd_phase", "") if smc_feat else "",
        "reasoning": reasoning,
        "indicators": {
            "RSI": features.get("RSI", {}).get("value"),
            "MACD": features.get("MACD", {}).get("signal"),
            "ADX": features.get("ADX", {}).get("value"),
            "EMA_signal": features.get("EMA", {}).get("signal"),
        },
        "source": "real-data",
    }
