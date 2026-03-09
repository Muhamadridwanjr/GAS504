import httpx
import pandas as pd
from typing import Optional
from src.config import settings
from src.lib.logger import logger

class MarketDataClient:
    def __init__(self):
        self.base_url = settings.market_data_url

    async def get_ohlc(self, symbol: str, timeframe: str = "H1", limit: int = 200) -> Optional[pd.DataFrame]:
        """
        Fetch OHLC data from the feature engine / market data processor.
        """
        try:
            # Reusing the feature engine endpoint format we created previously
            # Or market data processor url format
            # Depending on mapping. Assuming market data processor format for history:
            async with httpx.AsyncClient() as client:
                res = await client.get(
                    f"{self.base_url}/data/{symbol}",
                    params={"timeframe": timeframe, "limit": limit},
                    timeout=10.0
                )
                
            if res.status_code == 200:
                data = res.json()
                if not data or not isinstance(data, list):
                    return None
                
                df = pd.DataFrame(data)
                return df
            else:
                logger.error(f"Failed to fetch historical data for {symbol}: {res.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error fetching OHLC: {e}")
            return None

    async def get_latest_price(self, symbol: str) -> Optional[float]:
        """
        Fetch the most recent close price for a symbol.
        """
        df = await self.get_ohlc(symbol, limit=1)
        if df is not None and not df.empty and 'close' in df.columns:
            return float(df.iloc[-1]['close'])
        return None

market_client = MarketDataClient()
