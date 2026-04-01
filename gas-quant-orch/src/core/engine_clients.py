import httpx
from typing import Dict, Any, Optional
from src.config import settings
from src.lib.logger import logger

class EngineClients:
    def __init__(self):
        self.timeout = settings.request_timeout

    async def fetch_features(self, symbol: str, timeframe: str) -> Optional[Dict[str, Any]]:
        return await self._get(f"{settings.feature_engine_url}/features", {"symbol": symbol, "timeframe": timeframe})

    async def fetch_regime(self, symbol: str, timeframe: str, features: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        payload = {"symbol": symbol, "timeframe": timeframe, "features": features or {}}
        return await self._post(f"{settings.regime_detector_url}/regime", payload)

    async def fetch_pattern(self, symbol: str, timeframe: str) -> Optional[Dict[str, Any]]:
        payload = {"symbol": symbol, "timeframe": timeframe, "features": []}
        result = await self._post(f"{settings.pattern_detector_url}/detect", payload)
        if result and "direction" in result and "expected_direction" not in result:
            # Normalize field name for scorer compatibility
            result["expected_direction"] = result["direction"]
        return result

    async def fetch_statarb(self, pair: str) -> Optional[Dict[str, Any]]:
        payload = {"pair": pair}
        return await self._post(f"{settings.statarb_engine_url}/signal", payload)

    async def fetch_trend(self, symbol: str, timeframe: str) -> Optional[Dict[str, Any]]:
        payload = {"symbol": symbol, "timeframe": timeframe}
        return await self._post(f"{settings.trend_engine_url}/trend", payload)

    async def fetch_market_phase(self, symbol: str, timeframe: str) -> Optional[Dict[str, Any]]:
        payload = {"symbol": symbol, "timeframe": timeframe}
        return await self._post(f"{settings.market_phase_url}/phase", payload)

    async def fetch_orderflow(self, symbol: str) -> Optional[Dict[str, Any]]:
        return await self._get(f"{settings.orderflow_url}/orderflow/{symbol}/signal", {})

    async def _get(self, url: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(url, params=params, timeout=self.timeout)
                if res.status_code == 200:
                    return res.json()
                logger.warning(f"Engine returned {res.status_code} for {url}")
        except Exception as e:
            logger.warning(f"Failed to reach engine at {url}: {e}")
        return None

    async def _post(self, url: str, json_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(url, json=json_data, timeout=self.timeout)
                if res.status_code == 200:
                    return res.json()
                logger.warning(f"Engine returned {res.status_code} for {url}")
        except Exception as e:
            logger.warning(f"Failed to reach engine at {url}: {e}")
        return None

engine_clients = EngineClients()
