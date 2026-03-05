"""
GET /terminal/news – Latest market news.
"""
from fastapi import APIRouter
from src.config import settings
from src.services.client import fetch_json

router = APIRouter()

FALLBACK_NEWS = [
    {"title": "🔥 FED beri sinyal tahan suku bunga Q3", "source": "Reuters", "time": "2h ago"},
    {"title": "📈 Emas melonjak usai rilis data CPI rendah", "source": "Bloomberg", "time": "3h ago"},
    {"title": "🚀 BTC tembus resistensi kuat $65k", "source": "CoinDesk", "time": "4h ago"},
    {"title": "💡 Pasar global reli didorong sektor teknologi", "source": "CNBC", "time": "5h ago"},
    {"title": "⚡ NVIDIA catat rekor pendapatan Q4", "source": "MarketWatch", "time": "6h ago"},
]


@router.get("/terminal/news")
async def get_news():
    """Get latest market news."""
    data = await fetch_json(f"{settings.CALENDAR_NEWS_URL}/news/latest")
    if "error" in data or not isinstance(data, list):
        return {"status": "ok", "news": FALLBACK_NEWS}
    return {"status": "ok", "news": data}
