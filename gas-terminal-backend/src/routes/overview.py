"""
GET /terminal/overview – Aggregated dashboard data.
Returns prices, latest signal, news, macro data, AI analysis, and indices.
"""
import random
from fastapi import APIRouter, Request
from src.config import settings
from src.services.client import fetch_json

router = APIRouter()

# ── Fallback data (used when upstream services are unavailable) ─────
FALLBACK_PAIRS = [
    {"symbol": "XAUUSD", "name": "Gold / USD", "base": 2034.50, "vol": 0.8, "type": "Commodity",
     "trend": [30, 45, 40, 60, 55, 75, 70, 65, 80, 75]},
    {"symbol": "BTCUSD", "name": "Bitcoin / USD", "base": 64230.15, "vol": 25.0, "type": "Crypto",
     "trend": [50, 40, 70, 60, 90, 80, 100, 85, 95, 90]},
    {"symbol": "NVDA", "name": "NVIDIA Corp.", "base": 176.32, "vol": 1.5, "type": "Stock",
     "trend": [60, 55, 65, 75, 70, 85, 90, 80, 88, 92]},
    {"symbol": "EURUSD", "name": "Euro / USD", "base": 1.0854, "vol": 0.0006, "type": "Forex",
     "trend": [20, 25, 22, 30, 28, 35, 32, 38, 30, 36]},
    {"symbol": "TSLA", "name": "Tesla Inc.", "base": 247.10, "vol": 3.2, "type": "Stock",
     "trend": [80, 70, 75, 65, 60, 70, 80, 75, 85, 78]},
    {"symbol": "USDJPY", "name": "USD / Yen", "base": 149.85, "vol": 0.12, "type": "Forex",
     "trend": [40, 50, 45, 55, 60, 58, 65, 62, 70, 67]},
]

FALLBACK_INDICES = [
    {"name": "S&P 500", "value": 5274.39, "change": -14.39, "pct": -0.27},
    {"name": "DOW30", "value": 38772.81, "change": -213.81, "pct": -0.55},
    {"name": "HANGSENG", "value": 25183.57, "change": 123.57, "pct": 0.49},
    {"name": "NIKKEI225", "value": 40142.15, "change": 122.15, "pct": 0.31},
    {"name": "SHANGHAI", "value": 3829.23, "change": -12.23, "pct": -0.32},
    {"name": "FTSE", "value": 9624.89, "change": -122.89, "pct": -1.26},
]

FALLBACK_NEWS = [
    "🔥 FED beri sinyal tahan suku bunga Q3",
    "📈 Emas melonjak usai rilis data CPI rendah",
    "🚀 BTC tembus resistensi kuat $65k",
    "💡 Pasar global reli didorong sektor teknologi",
    "⚡ NVIDIA catat rekor pendapatan Q4",
]

FALLBACK_MACRO = [
    {"title": "Fed Rate", "value": "5.50%", "impact": "HIGH", "bias": "BEARISH USD"},
    {"title": "CPI YoY", "value": "3.2%", "impact": "HIGH", "bias": "BULLISH GOLD"},
    {"title": "NFP", "value": "187K", "impact": "MEDIUM", "bias": "USD NEUTRAL"},
    {"title": "DXY", "value": "104.2", "impact": "MEDIUM", "bias": "USD STRONG"},
]

FALLBACK_AI = {
    "trend": "BULLISH",
    "strength": 8.7,
    "logic": [
        "Liquidity sweep terdeteksi di 2028.50",
        "Order block tervalidasi pada H1",
        "Momentum bullish divergence (RSI)",
    ],
}


def _generate_signal(pair_symbol: str) -> dict:
    """Generate a simulated signal for a pair."""
    pair = next((p for p in FALLBACK_PAIRS if p["symbol"] == pair_symbol), FALLBACK_PAIRS[0])
    sig_type = "BUY" if random.random() > 0.45 else "SELL"
    score = random.random() * 10
    precision = 4 if pair["type"] == "Forex" else 2
    entry = round(pair["base"] + (random.random() - 0.5) * pair["vol"] * 10, precision)
    return {
        "id": f"sig-{random.randint(100000, 999999)}",
        "pair": pair_symbol,
        "type": sig_type,
        "grade": "A+" if score > 9 else "A" if score > 7 else "B+",
        "level": "HOT" if score > 9 else "VALID" if score > 7 else "WAIT",
        "entry": str(entry),
        "sl": str(round(entry * (0.990 if sig_type == "BUY" else 1.010), precision)),
        "tp1": str(round(entry * (1.015 if sig_type == "BUY" else 0.985), precision)),
        "tp2": str(round(entry * (1.028 if sig_type == "BUY" else 0.972), precision)),
        "confidence": random.randint(7, 9),
        "rr": "1:2.5",
    }


@router.get("/terminal/overview")
async def get_overview(request: Request):
    """
    Returns aggregated dashboard overview.
    Tries to fetch from upstream services; falls back to simulated data.
    """
    # Try fetching real signal from signal service
    signal_data = await fetch_json(f"{settings.SIGNAL_SERVICE_URL}/signal/latest?pair=XAUUSD")
    if "error" in signal_data:
        signal_data = _generate_signal("XAUUSD")

    # Try fetching news
    news_data = await fetch_json(f"{settings.CALENDAR_NEWS_URL}/news/latest")
    if "error" in news_data or not isinstance(news_data, list):
        news_data = FALLBACK_NEWS

    # Try fetching macro/fundamental data
    macro_data = await fetch_json(f"{settings.FUNDAMENTAL_DATA_URL}/fundamental/macro")
    if "error" in macro_data or not isinstance(macro_data, list):
        macro_data = FALLBACK_MACRO

    # Build pairs with simulated prices
    pairs = []
    for p in FALLBACK_PAIRS:
        price = p["base"] + (random.random() - 0.5) * p["vol"] * 5
        precision = 4 if p["type"] == "Forex" else 2
        pairs.append({**p, "price": round(price, precision)})

    return {
        "status": "ok",
        "pairs": pairs,
        "signal": signal_data,
        "news": news_data,
        "indices": FALLBACK_INDICES,
        "macro": macro_data,
        "ai": FALLBACK_AI,
    }
