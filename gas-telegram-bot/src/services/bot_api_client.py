"""
GAS Bot API Client — calls gas-web-backend internal bot endpoints.
All requests carry X-Bot-Key header for authentication.
"""
import httpx
from src.config import settings
from src.utils.logger import logger

_client: httpx.AsyncClient | None = None

HEADERS = {"X-Bot-Key": settings.BOT_API_KEY}


def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            base_url=settings.WEB_BACKEND_URL,
            headers=HEADERS,
            timeout=30.0,
        )
    return _client


async def analyze(
    gas_user_id: str,
    pair: str,
    style: str,
    feature: str = "technical",
    ai_tier: str = "basic",
) -> dict:
    """Legacy unified analyze endpoint (still used as fallback)."""
    try:
        c = _get_client()
        resp = await c.post("/api/v1/bot/analyze", json={
            "gas_user_id": gas_user_id,
            "pair": pair,
            "style": style,
            "feature": feature,
            "ai_tier": ai_tier,
        })
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error("bot_analyze_failed", error=str(e))
        return {"error": str(e)}


async def signal(gas_user_id: str, pair: str, style: str, ai_tier: str = "basic") -> dict:
    """Signal pipeline: indicator + strategy-core signal + calendar warning."""
    try:
        c = _get_client()
        resp = await c.post("/api/v1/bot/signal", json={
            "gas_user_id": gas_user_id, "pair": pair,
            "style": style, "ai_tier": ai_tier,
        })
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error("bot_signal_failed", error=str(e))
        return {"error": str(e)}


async def deep_analysis(gas_user_id: str, pair: str, style: str, ai_tier: str = "advanced") -> dict:
    """Analysis pipeline: technical MTF + calendar + correlation."""
    try:
        c = _get_client()
        resp = await c.post("/api/v1/bot/analysis", json={
            "gas_user_id": gas_user_id, "pair": pair,
            "style": style, "ai_tier": ai_tier,
        })
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error("bot_analysis_failed", error=str(e))
        return {"error": str(e)}


async def full_analyst(gas_user_id: str, pair: str, style: str, ai_tier: str = "pro") -> dict:
    """Analyst pipeline: hybrid + fundamental + trend + market phase."""
    try:
        c = _get_client()
        resp = await c.post("/api/v1/bot/analyst", json={
            "gas_user_id": gas_user_id, "pair": pair,
            "style": style, "ai_tier": ai_tier,
        })
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error("bot_analyst_failed", error=str(e))
        return {"error": str(e)}


async def close():
    global _client
    if _client:
        await _client.aclose()
        _client = None
