"""HTTP client for gas-smc-engine."""
import httpx
from src.config import settings
from src.lib.logger import get_logger
logger = get_logger(__name__)

class SMCClient:
    def __init__(self):
        self.base_url = settings.SMC_ENGINE_URL.rstrip("/")
        self.timeout = settings.REQUEST_TIMEOUT

    async def detect(self, symbol: str, timeframe: str) -> dict:
        url = f"{self.base_url}/detect"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, json={"symbol": symbol, "timeframe": timeframe})
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPError as e:
            logger.error("SMC error: %s", e)
            return {}
