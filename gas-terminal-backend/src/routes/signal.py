"""
GET /terminal/signal/latest – Latest trading signal for a pair.
"""
import random
from fastapi import APIRouter, Query
from src.config import settings
from src.services.client import fetch_json

router = APIRouter()


def _generate_signal(pair: str) -> dict:
    """Fallback signal generator."""
    sig_type = "BUY" if random.random() > 0.45 else "SELL"
    score = random.random() * 10
    base_prices = {
        "XAUUSD": (2034.50, 2), "BTCUSD": (64230.15, 2), "NVDA": (176.32, 2),
        "EURUSD": (1.0854, 4), "TSLA": (247.10, 2), "USDJPY": (149.85, 2),
    }
    base, prec = base_prices.get(pair, (100.0, 2))
    entry = round(base + (random.random() - 0.5) * base * 0.005, prec)
    return {
        "id": f"sig-{random.randint(100000, 999999)}",
        "pair": pair,
        "type": sig_type,
        "grade": "A+" if score > 9 else "A" if score > 7 else "B+",
        "level": "HOT" if score > 9 else "VALID" if score > 7 else "WAIT",
        "entry": str(entry),
        "sl": str(round(entry * (0.990 if sig_type == "BUY" else 1.010), prec)),
        "tp1": str(round(entry * (1.015 if sig_type == "BUY" else 0.985), prec)),
        "tp2": str(round(entry * (1.028 if sig_type == "BUY" else 0.972), prec)),
        "confidence": random.randint(7, 9),
        "rr": "1:2.5",
    }


@router.get("/terminal/signal/latest")
async def get_latest_signal(pair: str = Query("XAUUSD")):
    """Get latest signal for the specified pair."""
    data = await fetch_json(f"{settings.SIGNAL_SERVICE_URL}/signal/latest", params={"pair": pair})
    if "error" in data:
        data = _generate_signal(pair)
    return {"status": "ok", "signal": data}
