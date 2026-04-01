"""
GAS Memecoin Scoring Engine.
Composite score 0-100 from multiple signals.
Signal types: BUY EARLY | BUY MOMENTUM | WEAK TREND | AVOID | EXIT NOW | DANGER
"""
from typing import Dict, Any, Tuple

SIGNAL_THRESHOLDS = {
    "BUY EARLY":    (80, "🔥"),
    "BUY MOMENTUM": (65, "🚀"),
    "WEAK TREND":   (50, "📊"),
    "AVOID":        (35, "⚠️"),
    "EXIT NOW":     (20, "🚨"),
    "DANGER":       (0,  "💀"),
}

RISK_LEVELS = {
    "LOW":     (80, "#10b981"),
    "MEDIUM":  (60, "#f59e0b"),
    "HIGH":    (40, "#f97316"),
    "EXTREME": (0,  "#f43f5e"),
}


def score_token(token: Dict[str, Any], rug: Dict[str, Any]) -> Tuple[int, str, str]:
    """
    Calculate composite score, signal, and risk level.
    Returns: (score: int, signal: str, risk: str)
    """
    score = 0

    liq    = token.get("liquidity_usd", 0)
    vol1h  = token.get("volume_1h", 0)
    vol24  = token.get("volume_24h", 0)
    bp     = token.get("buy_pressure", 0.5)
    pc5m   = token.get("price_change_5m", 0)
    pc1h   = token.get("price_change_1h", 0)
    age    = token.get("age_minutes", 0)
    buys   = token.get("buys_1h", 0)
    rug_sc = rug.get("score", 50)

    # ── 1. Rug safety (20 pts) ────────────────────────────────────────────
    score += int(rug_sc * 0.20)

    # ── 2. Volume momentum (20 pts) ───────────────────────────────────────
    if vol1h > 100000:
        score += 20
    elif vol1h > 50000:
        score += 16
    elif vol1h > 10000:
        score += 12
    elif vol1h > 2000:
        score += 6
    else:
        score += 0

    # ── 3. Buy pressure (20 pts) ──────────────────────────────────────────
    if 0.60 <= bp <= 0.85:
        score += 20   # healthy bullish, not too extreme
    elif bp > 0.85:
        score += 10   # too one-sided, possible pump trap
    elif bp >= 0.50:
        score += 12
    else:
        score += 0    # selling pressure

    # ── 4. Price action (20 pts) ──────────────────────────────────────────
    if 5 <= pc1h <= 50 and pc5m > 0:
        score += 20   # steady uptrend
    elif pc1h > 50 and pc1h < 200:
        score += 14   # strong move, watch carefully
    elif 0 < pc1h <= 5:
        score += 10   # mild positive
    elif pc1h < -20:
        score += 0    # downtrend
    elif pc1h > 200:
        score += 5    # extreme pump = risky

    # ── 5. Liquidity (20 pts) ─────────────────────────────────────────────
    if liq >= 200000:
        score += 20
    elif liq >= 50000:
        score += 16
    elif liq >= 20000:
        score += 10
    elif liq >= 10000:
        score += 5
    else:
        score += 0

    # Penalties
    if rug["level"] == "DANGER":
        score = min(score, 35)   # cap score for DANGER tokens
    elif rug["level"] == "RISKY":
        score = min(score, 65)

    score = max(0, min(100, score))

    # Signal
    if rug["level"] == "DANGER":
        signal = "DANGER"
    elif score >= 80:
        signal = "BUY EARLY"
    elif score >= 65:
        signal = "BUY MOMENTUM"
    elif score >= 50:
        signal = "WEAK TREND"
    elif score >= 35:
        signal = "AVOID"
    elif score >= 20:
        signal = "EXIT NOW"
    else:
        signal = "DANGER"

    # Risk level
    if score >= 80 and rug["level"] == "SAFE":
        risk = "LOW"
    elif score >= 60 and rug["level"] in ("SAFE", "RISKY"):
        risk = "MEDIUM"
    elif score >= 40:
        risk = "HIGH"
    else:
        risk = "EXTREME"

    return score, signal, risk
