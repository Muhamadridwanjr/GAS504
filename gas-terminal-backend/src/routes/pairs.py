"""
GET /terminal/pairs – List all tradeable pairs with current prices.
"""
import random
from fastapi import APIRouter
from src.config import settings
from src.services.client import fetch_json

router = APIRouter()

PAIRS = [
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


@router.get("/terminal/pairs")
async def get_pairs():
    """Return all pairs with simulated current prices."""
    # Try to get real prices from MT5 data service
    live_data = await fetch_json(f"{settings.MT5_DATA_URL}/prices")

    result = []
    for p in PAIRS:
        precision = 4 if p["type"] == "Forex" else 2
        if isinstance(live_data, dict) and "error" not in live_data:
            price = live_data.get(p["symbol"], p["base"])
        else:
            price = p["base"] + (random.random() - 0.5) * p["vol"] * 5
        result.append({**p, "price": round(price, precision)})

    return {"status": "ok", "pairs": result}
