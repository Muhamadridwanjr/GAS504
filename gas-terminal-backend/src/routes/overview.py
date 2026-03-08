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
    {"symbol": "XAUUSD", "name": "Gold / USD", "base": 5089.872, "vol": 0.5, "type": "Commodity", "trend": [30, 45, 40, 60, 55, 75, 70, 65, 80, 75]},
    {"symbol": "BTCUSD", "name": "Bitcoin / USD", "base": 68783.71, "vol": 50.0, "type": "Crypto", "trend": [50, 40, 70, 60, 90, 80, 100, 85, 95, 90]},
    {"symbol": "EURUSD", "name": "Euro / USD", "base": 1.15554, "vol": 0.0001, "type": "Forex", "trend": [20, 25, 22, 30, 28, 35, 32, 38, 30, 36]},
    {"symbol": "GBPUSD", "name": "Pound / USD", "base": 1.33359, "vol": 0.0001, "type": "Forex", "trend": [40, 45, 42, 50, 48, 55, 52, 58, 50, 56]},
    {"symbol": "USDJPY", "name": "USD / Yen", "base": 157.880, "vol": 0.01, "type": "Forex", "trend": [40, 50, 45, 55, 60, 58, 65, 62, 70, 67]},
    {"symbol": "ETHUSD", "name": "Ethereum / USD", "base": 2005.41, "vol": 2.0, "type": "Crypto", "trend": [70, 65, 75, 85, 80, 95, 100, 90, 98, 92]},
    {"symbol": "XAGUSD", "name": "Silver / USD", "base": 82.454, "vol": 0.01, "type": "Commodity", "trend": [60, 55, 65, 75, 70, 85, 90, 80, 88, 92]},
    {"symbol": "US30", "name": "Dow Jones 30", "base": 47330.4, "vol": 20.0, "type": "Index", "trend": [80, 75, 85, 95, 90, 105, 110, 100, 108, 112]},
    {"symbol": "US500", "name": "S&P 500", "base": 6737.78, "vol": 5.0, "type": "Index", "trend": [90, 85, 95, 105, 100, 115, 120, 110, 118, 122]},
    {"symbol": "DXY", "name": "US Dollar Index", "base": 99.345, "vol": 0.05, "type": "Index", "trend": [50, 45, 55, 65, 60, 75, 80, 70, 78, 82]},
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
    "⚔️ Konflik AS-Iran menutup Selat Hormuz, minyak WTI tembus $88/bbl.",
    "📉 NFP AS anjlok ke -92.000, terburuk dalam beberapa bulan terakhir, picu ketakutan resesi.",
    "🏦 The Fed pertahankan suku bunga 3.50%-3.75%, terjebak dalam stagflasi.",
    "⚠️ VIX melonjak di atas 25 mencerminkan kepanikan pasar global (Risk-Off).",
    "🏛️ Suku bunga BOJ tertahan di 0.75%, level tertinggi dalam 30 tahun terakhir.",
    "🪙 Emas cetak rekor di sekitar $5,150/oz didukung permintaan safe-haven yang sangat kuat."
]

FALLBACK_MACRO = [
    {"title": "Suku Bunga The Fed", "value": "3.50-3.75%", "impact": "HIGH", "bias": "DITAHAN"},
    {"title": "CPI AS (y/y)", "value": "2.4%", "impact": "HIGH", "bias": "BULLISH EMAS"},
    {"title": "NFP AS", "value": "-92K", "impact": "HIGH", "bias": "BEARISH USD"},
    {"title": "Yield Obligasi 10Y", "value": "4.15%", "impact": "HIGH", "bias": "BULLISH USD"},
    {"title": "Minyak WTI", "value": "$88/bbl", "impact": "HIGH", "bias": "BULLISH MINYAK"},
    {"title": "Suku Bunga ECB", "value": "2.15%", "impact": "HIGH", "bias": "DITAHAN"},
    {"title": "Suku Bunga BOJ", "value": "0.75%", "impact": "HIGH", "bias": "DITAHAN"},
    {"title": "Inflasi Inggris", "value": "3.0%", "impact": "HIGH", "bias": "NEUTRAL"},
    {"title": "Indeks VIX", "value": "25.26", "impact": "HIGH", "bias": "RISK-OFF"},
]

FALLBACK_AI = {
    "trend": "STAGFLASI / RISK-OFF",
    "strength": 9.2,
    "logic": [
        "Konflik AS-Iran (Op Epic Fury) menutup Selat Hormuz, suplai minyak terancam.",
        "Data NFP rilis di -92.000, memicu kekhawatiran resesi yang mendalam.",
        "The Fed terjebak stagflasi: inflasi ditekan minyak, namun pertumbuhan lambat.",
        "Aset Safe-haven (Emas $5,150) dan Indeks Dolar (DXY 99.34) menguat drastis."
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
