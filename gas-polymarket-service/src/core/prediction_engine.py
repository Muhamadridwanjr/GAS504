"""GAS Prediction Engine — single-model YES/NO probability with pre-filter."""
import httpx
import logging
from typing import Dict, Any, Optional
from ..config import settings

logger = logging.getLogger("prediction_engine")

# Pre-filter: skip boring events
def should_skip(tech: Dict[str, Any]) -> bool:
    """Return True if market is too neutral to predict (save AI cost)."""
    summary = tech.get("summary", {})
    buy = summary.get("buy", 0)
    sell = summary.get("sell", 0)
    neutral = summary.get("neutral", 0)
    total = buy + sell + neutral or 1
    neutral_pct = neutral / total
    # Skip if >65% neutral signals (ranging)
    return neutral_pct > 0.65

def _signal_strength(yes: float) -> str:
    """Map YES probability to signal strength label."""
    if yes >= 78:
        return "STRONG BUY YES"
    if yes >= 65:
        return "BUY YES"
    if yes >= 55:
        return "WEAK YES"
    if yes <= 22:
        return "STRONG BUY NO"
    if yes <= 35:
        return "BUY NO"
    if yes <= 45:
        return "WEAK NO"
    return "NO TRADE"

async def predict_single(
    question: str,
    category: str,
    yes_price: float,
    no_price: float,
    pair: Optional[str] = None,
    model: str = "claude",
) -> Dict[str, Any]:
    """
    Call strategy-core for technical bias, combine with market price,
    produce YES/NO probability with signal strength.
    """
    # Choose timeframe based on question content
    q_lower = question.lower()
    if any(k in q_lower for k in ["4h", "4 hour", "4hours"]):
        timeframe = "H4"
    elif any(k in q_lower for k in ["today", "hari ini", "day", "session", "open", "close"]):
        timeframe = "H1"
    elif any(k in q_lower for k in ["week", "weekly", "minggu"]):
        timeframe = "D1"
    else:
        timeframe = "H4"

    # Map pair to strategy-core format
    tf_pair = pair or "XAUUSD"
    if "/" in tf_pair:
        tf_pair = tf_pair.replace("/", "")  # BTC/USDT → BTCUSDT

    tech: Dict[str, Any] = {}
    skipped = False
    try:
        payload = {
            "pair": tf_pair,
            "timeframe": timeframe,
            "style": "intraday",
            "indicators": ["RSI", "MACD", "ADX", "BB", "EMA20", "EMA50", "STOCH"],
            "model": model,
        }
        async with httpx.AsyncClient(timeout=12.0) as client:
            resp = await client.post(
                f"{settings.STRATEGY_CORE_URL}/v1/analysis/technical",
                json=payload,
            )
            if resp.status_code == 200:
                tech = resp.json()
    except Exception as e:
        logger.warning(f"strategy-core {model} error: {e}")

    # Pre-filter: skip ranging markets
    if should_skip(tech):
        skipped = True
        return {
            "yes": 50.0,
            "no": 50.0,
            "confidence": 40.0,
            "action": "NO TRADE",
            "signal_strength": "NO TRADE",
            "reasoning": f"Market ranging — {tf_pair} showing no clear directional bias. Skip.",
            "tech_bias": 0.0,
            "model": model,
            "skipped": True,
        }

    # Derive bias from technical result
    summary = tech.get("summary", {})
    buy_signals  = summary.get("buy",     0)
    sell_signals = summary.get("sell",    0)
    neutral      = summary.get("neutral", 0)
    total = buy_signals + sell_signals + neutral or 1
    tech_bias = (buy_signals - sell_signals) / total  # -1 to +1

    # Combine: market price 55% + tech bias 45%
    market_yes = float(yes_price)
    tech_yes = 0.5 + (tech_bias * 0.40)
    blended_yes = round(market_yes * 0.55 + tech_yes * 0.45, 4)
    blended_yes = max(0.05, min(0.95, blended_yes))

    # Confidence: distance from 50% + indicator agreement
    distance = abs(blended_yes - 0.5)
    agreement = abs(buy_signals - sell_signals) / total
    confidence = round(min(0.96, 0.45 + distance * 1.4 + agreement * 0.2), 4)

    # Build reasoning
    trend_word = "bullish" if tech_bias > 0.1 else "bearish" if tech_bias < -0.1 else "neutral"
    if blended_yes > 0.6:
        reasoning = (
            f"{trend_word.capitalize()} {tf_pair} ({buy_signals}B/{sell_signals}S/{neutral}N). "
            f"Market priced YES at {round(market_yes*100)}%. "
            f"Technical bias supports YES outcome on {timeframe}."
        )
    elif blended_yes < 0.4:
        reasoning = (
            f"{trend_word.capitalize()} bias on {tf_pair} ({sell_signals}S/{buy_signals}B). "
            f"Market YES only {round(market_yes*100)}%. "
            f"NO outcome more likely on {timeframe}."
        )
    else:
        reasoning = (
            f"Mixed signals on {tf_pair} ({buy_signals}B/{sell_signals}S/{neutral}N). "
            f"Market near 50/50 ({round(market_yes*100)}% YES). No clear edge — skip or wait."
        )

    return {
        "yes": round(blended_yes * 100, 1),
        "no": round((1.0 - blended_yes) * 100, 1),
        "confidence": round(confidence * 100, 1),
        "action": "BUY YES" if blended_yes >= 0.65 else ("BUY NO" if blended_yes <= 0.35 else "NO TRADE"),
        "signal_strength": _signal_strength(blended_yes * 100),
        "reasoning": reasoning,
        "tech_bias": round(tech_bias, 3),
        "model": model,
        "timeframe": timeframe,
        "skipped": False,
    }
