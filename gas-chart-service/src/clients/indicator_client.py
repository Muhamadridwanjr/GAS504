"""HTTP client for gas-indicator-engine."""
import httpx
from src.config import settings
from src.lib.logger import get_logger
logger = get_logger(__name__)

class IndicatorClient:
    def __init__(self):
        self.base_url = settings.INDICATOR_ENGINE_URL.rstrip("/")
        self.timeout = settings.REQUEST_TIMEOUT

    async def calculate(self, symbol: str, timeframe: str, indicators: list[dict]) -> dict:
        url = f"{self.base_url}/calculate"
        # Transform frontend indicators [{type, period}] to indicator-engine format [{name, periods}]
        mapped_indicators = []
        for ind in indicators:
            mapped_indicators.append({
                "name": ind.get("type", ind.get("name")),
                "periods": [ind.get("period")] if "period" in ind else ind.get("periods", [14])
            })
            
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, json={
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "indicators": mapped_indicators
                })
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPError as e:
            logger.error("Indicator error: %s", e)
            return {}
