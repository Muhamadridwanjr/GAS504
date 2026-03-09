import json
from src.redis_client.client import redis_client
from src.models.messages import TickMessage, OhlcMessage
from src.config import settings
from src.lib.logger import log

class DataForwarder:
    @staticmethod
    async def forward_tick(tick: TickMessage):
        """Forwards tick data to Redis"""
        channel = settings.REDIS_TICK_CHANNEL
        payload = tick.model_dump_json()
        await redis_client.publish(channel, payload)
        
    @staticmethod
    async def forward_ohlc(ohlc: OhlcMessage):
        """Forwards OHLC data to Redis"""
        channel = f"{settings.REDIS_OHLC_CHANNEL_PREFIX}:{ohlc.symbol}:{ohlc.timeframe}"
        payload = ohlc.model_dump_json()
        await redis_client.publish(channel, payload)

forwarder = DataForwarder()
