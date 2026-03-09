from src.clients.feature_client import FeatureClient
from src.core.rules import detect_phase
from src.api.models import PhaseResponse, PhaseDetails
from src.cache.redis_cache import cache
from src.lib.logger import get_logger

logger = get_logger(__name__)

class PhaseDetector:
    def __init__(self):
        self.feature_client = FeatureClient()

    async def get_phase(self, symbol: str, timeframe: str) -> PhaseResponse:
        cache_key = f"phase:{symbol}:{timeframe}"
        
        # Check cache
        cached_result = await cache.get(cache_key)
        if cached_result:
            logger.info(f"Returning cached phase for {symbol} {timeframe}")
            return PhaseResponse(**cached_result)

        # Fetch features
        logger.info(f"Calculating phase for {symbol} {timeframe}")
        features = await self.feature_client.get_latest_features(symbol, timeframe)
        
        # Apply Rules
        phase_name, confidence, details_dict = detect_phase(features)
        
        details = PhaseDetails(**details_dict)
        response = PhaseResponse(
            symbol=symbol,
            timeframe=timeframe,
            phase=phase_name,
            confidence=confidence,
            details=details
        )
        
        # Save to cache
        await cache.set(cache_key, response.model_dump())
        
        return response
