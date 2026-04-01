import asyncio
import json
import websockets
import logging
from ..core.publisher import publisher

logger = logging.getLogger("websocket_manager")

# Crypto Major 10 + extended large-cap + new listings (Spot)
SPOT_PAIRS = [
    # Crypto Major 10
    "btcusdt", "ethusdt", "bnbusdt", "solusdt", "xrpusdt",
    "adausdt", "dogeusdt", "trxusdt", "dotusdt", "maticusdt",
    # Extended large-cap
    "linkusdt", "avaxusdt", "ltcusdt", "uniusdt", "atomusdt",
    "nearusdt", "arbusdt", "opusdt", "injusdt", "aptusdt",
    "suiusdt", "seiusdt", "imxusdt", "fetusdt", "rndrusdt",
    "tonusdt", "shibusdt", "icpusdt", "filusdt", "stxusdt",
    # New listings
    "jupusdt", "wifusdt", "enausdt", "notusdt", "catiusdt",
    "bomeusdt", "dogsusdt", "pepeusdt", "eigenusdt", "hmstrusdt",
]

# Crypto Major 10 + extended + new listings (USDT-M Futures)
FUTURES_PAIRS = [
    # Crypto Major 10
    "btcusdt", "ethusdt", "bnbusdt", "solusdt", "xrpusdt",
    "adausdt", "dogeusdt", "trxusdt", "dotusdt", "maticusdt",
    # Extended
    "linkusdt", "avaxusdt", "ltcusdt", "uniusdt", "atomusdt",
    "nearusdt", "arbusdt", "opusdt", "injusdt", "aptusdt",
    "suiusdt", "seiusdt", "tiausdt", "fetusdt", "rndrusdt",
    # Meme / new listings
    "wifusdt", "pepeusdt", "flokiusdt", "wldusdt", "blurusdt",
    "shibusdt", "bonkusdt", "enausdt", "jupusdt", "notusdt",
]

PAIRS_BY_MARKET = {
    "spot": SPOT_PAIRS,
    "usdt_futures": FUTURES_PAIRS,
}


class BinanceWebSocketManager:
    def __init__(self):
        self.spot_url = "wss://stream.binance.com:9443/ws"
        self.usdt_futures_url = "wss://fstream.binance.com/ws"
        self.coin_futures_url = "wss://dstream.binance.com/ws"
        self.tasks = []
        self.running = False
        self.subscriptions = set()

    async def start(self):
        self.running = True
        logger.info("Starting WebSocket Manager...")
        self.tasks.append(asyncio.create_task(self._connect_and_listen(self.spot_url, "spot")))
        self.tasks.append(asyncio.create_task(self._connect_and_listen(self.usdt_futures_url, "usdt_futures")))

    async def stop(self):
        self.running = False
        for task in self.tasks:
            task.cancel()
        logger.info("WebSocket Manager stopped.")

    async def _connect_and_listen(self, url: str, market_type: str):
        pairs = PAIRS_BY_MARKET.get(market_type, SPOT_PAIRS)
        streams = [f"{p}@ticker" for p in pairs]

        while self.running:
            try:
                async with websockets.connect(url) as ws:
                    logger.info(f"Connected to Binance {market_type} WS ({len(pairs)} pairs)")

                    # Binance allows max 200 streams per connection; chunk if needed
                    for chunk_start in range(0, len(streams), 200):
                        chunk = streams[chunk_start:chunk_start + 200]
                        sub_msg = {
                            "method": "SUBSCRIBE",
                            "params": chunk,
                            "id": chunk_start + 1,
                        }
                        await ws.send(json.dumps(sub_msg))

                    while self.running:
                        msg = await ws.recv()
                        data = json.loads(msg)

                        if 'e' in data and data['e'] == '24hrTicker':
                            symbol = data['s']
                            # Normalize: BTCUSDT → BTC/USDT, futures → BTC/USDT:USDT
                            if symbol.endswith("USDT"):
                                norm_symbol = f"{symbol[:-4]}/USDT"
                            else:
                                norm_symbol = symbol
                            if market_type == "usdt_futures":
                                norm_symbol += ":USDT"

                            payload = {
                                "last": float(data.get('c', 0)),
                                "bid": float(data.get('b', 0)) if data.get('b') else 0.0,
                                "ask": float(data.get('a', 0)) if data.get('a') else 0.0,
                                "volume": float(data.get('v', 0)),
                                "change": float(data.get('p', 0)),
                                "changePercent": float(data.get('P', 0)),
                                "high": float(data.get('h', 0)),
                                "low": float(data.get('l', 0)),
                            }
                            await publisher.publish_tick(norm_symbol, payload)
            except Exception as e:
                logger.error(f"WS error on {market_type}: {e}")
                await asyncio.sleep(5)

ws_manager = BinanceWebSocketManager()
