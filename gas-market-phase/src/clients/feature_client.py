import httpx
from src.config import settings
from src.lib.logger import get_logger
from src.core.exceptions import PhaseEngineException

logger = get_logger(__name__)

class FeatureClient:
    def __init__(self):
        self.base_url = settings.FEATURE_ENGINE_URL

    async def get_latest_features(self, symbol: str, timeframe: str) -> dict:
        """
        Fetches the latest features necessary to determine market phase.
        Expected from gas-feature-engine (mocking logic here if it doesn't exist yet).
        We expect: price, ema50, adx, volume_ratio, low_20, high_20
        """
        # IN A REAL SCENARIO:
        # async with httpx.AsyncClient() as client:
        #     try:
        #         resp = await client.get(f"{self.base_url}/features/latest", params={"symbol": symbol, "timeframe": timeframe})
        #         resp.raise_for_status()
        #         return resp.json()
        #     except Exception as e:
        #         logger.error(f"Failed to fetch features for {symbol}: {e}")
        #         raise PhaseEngineException(f"Feature engine unavailable: {e}")

        # MOCK IMPLEMENTATION FOR NOW to ensure the engine runs independently if feature engine is not fully returning these exact fields:
        logger.info(f"Mocking feature fetch for {symbol} {timeframe}")
        return {
            "price": 2005.5,
            "ema50": 1990.0,
            "adx": 28.5,
            "volume_ratio": 1.5,
            "low_20": 1980.0,
            "high_20": 2010.0
        }
