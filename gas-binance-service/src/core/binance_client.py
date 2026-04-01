import ccxt.async_support as ccxt
import asyncio
from typing import Dict, Any, List
from ..config import settings

class BinanceClient:
    def __init__(self):
        self.spot = ccxt.binance({
            'apiKey': settings.binance_api_key,
            'secret': settings.binance_secret_key,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        
        self.usdt_futures = ccxt.binance({
            'apiKey': settings.binance_api_key,
            'secret': settings.binance_secret_key,
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}
        })
        
        self.coin_futures = ccxt.binance({
            'apiKey': settings.binance_api_key,
            'secret': settings.binance_secret_key,
            'enableRateLimit': True,
            'options': {'defaultType': 'delivery'}
        })

    async def load_markets(self):
        await asyncio.gather(
            self.spot.load_markets(),
            self.usdt_futures.load_markets(),
            self.coin_futures.load_markets()
        )

    async def close(self):
        await asyncio.gather(
            self.spot.close(),
            self.usdt_futures.close(),
            self.coin_futures.close()
        )

    def _get_client_for_symbol(self, symbol: str):
        if ":" in symbol:
            if symbol.endswith(":USDT"):
                return self.usdt_futures
            else:
                return self.coin_futures
        return self.spot

    async def fetch_ohlcv(self, symbol: str, timeframe: str, since: int = None, limit: int = None):
        client = self._get_client_for_symbol(symbol)
        limit = limit or settings.default_limit
        return await client.fetch_ohlcv(symbol, timeframe, since, limit)

    async def fetch_ticker(self, symbol: str):
        client = self._get_client_for_symbol(symbol)
        return await client.fetch_ticker(symbol)

    async def fetch_order_book(self, symbol: str, limit: int = 10):
        client = self._get_client_for_symbol(symbol)
        return await client.fetch_order_book(symbol, limit)

    async def fetch_tickers(self, symbols: List[str]):
        """Fetch multiple tickers in parallel by grouping them by market type."""
        groups = {}
        for sym in symbols:
            client = self._get_client_for_symbol(sym)
            groups.setdefault(client, []).append(sym)
        
        tasks = []
        for client, syms in groups.items():
            tasks.append(client.fetch_tickers(syms))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        merged = {}
        for res in results:
            if isinstance(res, dict):
                merged.update(res)
            # Ignore exceptions for individual groups to avoid failing the whole request
        return merged

    def get_supported_markets(self) -> Dict[str, List[str]]:
        return {
            "spot": list(self.spot.markets.keys()) if self.spot.markets else [],
            "usdt_futures": list(self.usdt_futures.markets.keys()) if self.usdt_futures.markets else [],
            "coin_futures": list(self.coin_futures.markets.keys()) if self.coin_futures.markets else []
        }

binance_client = BinanceClient()
