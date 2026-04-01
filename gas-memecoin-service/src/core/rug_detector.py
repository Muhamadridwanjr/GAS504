"""Rug Pull Detection Engine — heuristic-based on-chain signal analysis."""
from typing import Dict, Any, List, Tuple

# Weights for rug scoring (higher = safer)
RUG_CHECKS = {
    "liquidity_ok":      25,  # liq > $50k = safe
    "liquidity_medium":  10,  # liq $10-50k = ok
    "buy_pressure_ok":   15,  # buy > 55% = healthy
    "age_ok":            15,  # age 30-180 min = sweet spot
    "volume_legit":      15,  # vol not suspiciously uniform
    "tx_diversity":      15,  # buys + sells both present
    "price_stable":      15,  # not +1000% in 5m (pump trap)
}

def detect_rug(token: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze token for rug pull indicators.
    Returns: {level: SAFE|RISKY|DANGER, score: 0..100, flags: [...]}
    Higher score = SAFER.
    """
    flags: List[str] = []
    score = 0

    liq   = token.get("liquidity_usd", 0)
    vol1h = token.get("volume_1h", 0)
    vol24 = token.get("volume_24h", 0)
    buys  = token.get("buys_1h", 0)
    sells = token.get("sells_1h", 0)
    bp    = token.get("buy_pressure", 0.5)
    age   = token.get("age_minutes", 0)
    pc5m  = token.get("price_change_5m", 0)
    pc1h  = token.get("price_change_1h", 0)

    # ── Liquidity check ──────────────────────────────────────────────────
    if liq >= 50000:
        score += RUG_CHECKS["liquidity_ok"]
    elif liq >= 10000:
        score += RUG_CHECKS["liquidity_medium"]
        flags.append("Low liquidity (<$50k) — higher rug risk")
    else:
        flags.append("⚠️ Very low liquidity (<$10k) — DANGER")

    # ── Buy pressure ─────────────────────────────────────────────────────
    if bp >= 0.55:
        score += RUG_CHECKS["buy_pressure_ok"]
    elif bp <= 0.30:
        flags.append("Heavy sell pressure (sell > 70%) — possible exit")
    elif bp >= 0.90 and buys > 20:
        flags.append("⚠️ 90%+ buy pressure — possible coordinated pump trap")
        score -= 10

    # ── Token age ────────────────────────────────────────────────────────
    if 30 <= age <= 180:
        score += RUG_CHECKS["age_ok"]
    elif age < 10:
        flags.append("⚠️ Token < 10 min old — extreme risk")
        score -= 15
    elif age < 30:
        flags.append("Token < 30 min — very early, high risk")
    elif age > 1440:
        flags.append("Token > 24h — late entry risk")

    # ── Volume legitimacy ────────────────────────────────────────────────
    if vol1h > 5000 and vol24 > 0:
        vol_ratio = vol1h / max(vol24 / 24, 1)
        if 0.5 <= vol_ratio <= 8.0:
            score += RUG_CHECKS["volume_legit"]
        elif vol_ratio > 20:
            flags.append("⚠️ Unusual volume spike (20×) — possible manipulation")
        else:
            score += RUG_CHECKS["volume_legit"] // 2
    elif vol1h < 1000:
        flags.append("Very low 1h volume (<$1k)")

    # ── TX diversity ─────────────────────────────────────────────────────
    total_tx = buys + sells
    if total_tx >= 10 and sells >= 2:
        score += RUG_CHECKS["tx_diversity"]
    elif sells == 0 and buys > 5:
        flags.append("⚠️ Zero sell transactions — honeypot risk")
        score -= 20
    elif total_tx < 5:
        flags.append("Very few transactions — low confidence")

    # ── Price stability ──────────────────────────────────────────────────
    if abs(pc5m) < 30:
        score += RUG_CHECKS["price_stable"]
    elif pc5m > 100:
        flags.append("⚠️ +100% in 5min — likely pump trap")
        score -= 10
    elif pc5m < -50:
        flags.append("⚠️ -50% in 5min — dump in progress")
        score -= 15

    # ── Additional rug signals ───────────────────────────────────────────
    if pc1h > 500:
        flags.append("⚠️ +500% in 1h — extreme pump, exit risk high")
        score -= 10

    if liq < 5000:
        flags.append("🔴 Liquidity < $5k — DANGER: easy to rug")
        score -= 20

    # Clamp score
    score = max(0, min(100, score))

    # Determine level
    if score >= 65:
        level = "SAFE"
    elif score >= 40:
        level = "RISKY"
    else:
        level = "DANGER"

    return {
        "level": level,
        "score": score,
        "flags": flags,
    }
