"""
GAS Memecoin AI Engine — 4-model analysis.
Each model specializes in a different aspect of memecoin analysis.
"""
import httpx
import asyncio
import logging
from typing import Dict, Any, List, Optional
from ..config import settings

logger = logging.getLogger("memecoin_ai")

MODEL_SPEC = {
    "claude":  {"weight": 1.3, "specialty": "Rug Detection",   "color": "#f59e0b"},
    "gpt":     {"weight": 1.2, "specialty": "Volume Analysis",  "color": "#10b981"},
    "gemini":  {"weight": 1.0, "specialty": "Pattern & Trend",  "color": "#3b82f6"},
    "grok":    {"weight": 0.8, "specialty": "Momentum & FOMO",  "color": "#f43f5e"},
}

MODEL_FOCUS = {
    "claude":  "rug pull detection and safety analysis",
    "gpt":     "volume patterns and market microstructure",
    "gemini":  "price structure and trend analysis",
    "grok":    "momentum and FOMO detection",
}

SIGNAL_VALUES = {
    "BUY EARLY":    90,
    "BUY MOMENTUM": 72,
    "WEAK TREND":   50,
    "AVOID":        30,
    "EXIT NOW":     15,
    "DANGER":       0,
}

def _build_signal_from_score(score: int, rug_level: str) -> str:
    if rug_level == "DANGER":
        return "DANGER"
    if score >= 80:
        return "BUY EARLY"
    if score >= 65:
        return "BUY MOMENTUM"
    if score >= 50:
        return "WEAK TREND"
    if score >= 35:
        return "AVOID"
    if score >= 20:
        return "EXIT NOW"
    return "DANGER"


async def _ask_strategy_core(token: Dict[str, Any], model: str, rug: Dict[str, Any]) -> Dict[str, Any]:
    """Ask strategy-core for AI analysis of this memecoin."""
    focus = MODEL_FOCUS.get(model, "general analysis")

    # Build context payload — use BTC/USDT as proxy pair with token metrics injected
    context_prompt = (
        f"Memecoin: {token['symbol']} on {token['chain'].upper()}\n"
        f"Price change 1h: {token['price_change_1h']:+.1f}%\n"
        f"Price change 5m: {token['price_change_5m']:+.1f}%\n"
        f"Volume 1h: ${token['volume_1h']:,.0f}\n"
        f"Liquidity: ${token['liquidity_usd']:,.0f}\n"
        f"Buy pressure: {token['buy_pressure']*100:.0f}%\n"
        f"Age: {token['age_minutes']:.0f} minutes\n"
        f"Rug level: {rug['level']} (score {rug['score']}/100)\n"
        f"Rug flags: {'; '.join(rug['flags'][:3]) if rug['flags'] else 'None'}\n"
        f"Your focus: {focus}\n"
        f"Return: BUY EARLY / BUY MOMENTUM / WEAK TREND / AVOID / EXIT NOW / DANGER"
    )

    payload = {
        "pair": "BTC/USDT",
        "timeframe": "M5",
        "style": "scalping",
        "indicators": ["RSI", "MACD", "BB"],
        "model": model,
        "extra_context": context_prompt,
    }

    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            resp = await client.post(
                f"{settings.STRATEGY_CORE_URL}/v1/analysis/technical",
                json=payload,
            )
            if resp.status_code == 200:
                return resp.json()
    except Exception as e:
        logger.warning(f"strategy-core {model} error: {e}")
    return {}


async def run_ai_analysis(token: Dict[str, Any], rug: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Run 4-model AI analysis concurrently."""

    async def analyze_one(model: str) -> Dict[str, Any]:
        spec = MODEL_SPEC[model]
        tech = await _ask_strategy_core(token, model, rug)

        # Derive AI score from technical result + token metrics
        summary = tech.get("summary", {})
        buy_sigs  = summary.get("buy",     0)
        sell_sigs = summary.get("sell",    0)
        neutral   = summary.get("neutral", 0)
        total = buy_sigs + sell_sigs + neutral or 1
        tech_bias = (buy_sigs - sell_sigs) / total  # -1 to +1

        # Base score from token metrics
        base = 50 + tech_bias * 25

        # Adjust for model specialty
        bp = token.get("buy_pressure", 0.5)
        pc1h = token.get("price_change_1h", 0)
        liq = token.get("liquidity_usd", 0)

        if model == "claude":   # safety-focused
            adj = (rug["score"] / 100) * 20 - 10
        elif model == "gpt":    # volume-focused
            vol1h = token.get("volume_1h", 0)
            adj = min(15, (vol1h / 50000) * 15) - 5
        elif model == "gemini": # trend-focused
            adj = (pc1h / 100) * 10 if -50 < pc1h < 200 else -10
        else:                   # grok: momentum
            adj = (bp - 0.5) * 30

        ai_score = max(0, min(100, int(base + adj)))
        signal = _build_signal_from_score(ai_score, rug["level"])
        confidence = round(0.45 + abs(tech_bias) * 0.4 + abs(bp - 0.5) * 0.15, 2)

        # Reasoning
        if signal in ("BUY EARLY", "BUY MOMENTUM"):
            reasoning = (
                f"{spec['specialty']} → {buy_sigs}B/{sell_sigs}S signals. "
                f"Buy pressure {bp*100:.0f}%, +{pc1h:.0f}% 1h. "
                f"Rug: {rug['level']}. Looks {signal.lower()}."
            )
        elif signal == "DANGER":
            reasoning = f"DANGER — {'; '.join(rug['flags'][:2]) or 'extreme risk detected'}"
        else:
            reasoning = (
                f"{spec['specialty']} → mixed signals. "
                f"BP {bp*100:.0f}%, trend {pc1h:+.0f}% 1h. Caution advised."
            )

        return {
            "model":     model,
            "signal":    signal,
            "score":     ai_score,
            "confidence": round(min(0.97, confidence), 2),
            "reasoning": reasoning,
            "weight":    spec["weight"],
            "specialty": spec["specialty"],
            "color":     spec["color"],
        }

    results = await asyncio.gather(*[analyze_one(m) for m in MODEL_SPEC], return_exceptions=True)
    return [r for r in results if isinstance(r, dict)]


def build_ai_consensus(agents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Weighted consensus from 4 models."""
    if not agents:
        return {"signal": "AVOID", "confidence": 0.4}

    total_weight = sum(a.get("weight", 1.0) for a in agents)
    weighted_score = sum(
        SIGNAL_VALUES.get(a["signal"], 50) * a.get("weight", 1.0)
        for a in agents
    ) / total_weight

    avg_conf = sum(a["confidence"] * a.get("weight", 1.0) for a in agents) / total_weight

    # Majority-weighted vote
    danger_w = sum(a["weight"] for a in agents if a["signal"] == "DANGER")
    buy_w    = sum(a["weight"] for a in agents if a["signal"] in ("BUY EARLY", "BUY MOMENTUM"))
    avoid_w  = sum(a["weight"] for a in agents if a["signal"] in ("AVOID", "EXIT NOW"))

    if danger_w >= total_weight * 0.5:
        consensus = "DANGER"
    elif buy_w >= total_weight * 0.55 and weighted_score >= 65:
        consensus = "BUY EARLY" if weighted_score >= 80 else "BUY MOMENTUM"
    elif avoid_w >= total_weight * 0.55:
        consensus = "AVOID"
    elif weighted_score >= 50:
        consensus = "WEAK TREND"
    else:
        consensus = "AVOID"

    return {
        "signal":     consensus,
        "confidence": round(min(0.97, avg_conf), 2),
        "score":      round(weighted_score),
    }
