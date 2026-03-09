import httpx
import pandas as pd
from typing import Optional
from src.config import settings
from src.lib.logger import logger

class MarketDataClient:
    def __init__(self):
        self.base_url = settings.market_data_url

    async def get_ohlc(self, symbol: str, timeframe: str, limit: int = 100) -> Optional[pd.DataFrame]:
        """
        Fetch OHLC data from the market data processor.
        Returns a Pandas DataFrame or None if request fails.
        """
        try:
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
                
                # Convert to DataFrame
                df = pd.DataFrame(data)
                # Ensure columns exist
                for col in ['time', 'open', 'high', 'low', 'close', 'volume']:
                    if col not in df.columns:
                        if col == 'volume':
                            df['volume'] = 0.0
                        else:
                            df[col] = 0.0
                return df
            else:
                logger.error(f"Failed to fetch market data: {res.status_code} {res.text}")
                return None
        except Exception as e:
            logger.error(f"Error fetching OHLC: {e}")
            return None
