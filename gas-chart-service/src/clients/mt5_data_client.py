"""HTTP client for gas-mt5-data-service."""
import httpx
from src.config import settings
from src.lib.logger import get_logger
logger = get_logger(__name__)

class MT5DataClient:
    def __init__(self):
        self.base_url = settings.MT5_DATA_URL.rstrip("/")
        self.timeout = settings.REQUEST_TIMEOUT

    async def get_ohlc(self, symbol: str, timeframe: str, from_ts: int | None = None,
                       to_ts: int | None = None, count: int | None = None) -> list[dict]:
        url = f"{self.base_url}/history"
        params = {"symbol": symbol, "timeframe": timeframe}
        if from_ts: params["from_time"] = from_ts
        if to_ts: params["to_time"] = to_ts
        if count: params["count"] = count
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                return resp.json().get("data", resp.json().get("candles", []))
        except httpx.HTTPError as e:
            logger.error("MT5 data error: %s", e)
            return []
