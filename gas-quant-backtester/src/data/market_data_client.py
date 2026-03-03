import httpx
import pandas as pd
from typing import Optional
from src.config import settings
from src.lib.logger import logger

class MarketDataClient:
    def __init__(self):
        self.base_url = settings.market_data_url

    async def get_historical_data(self, symbol: str, timeframe: str, from_date: str, to_date: str) -> Optional[pd.DataFrame]:
        logger.info(f"Fetching historical data for {symbol} ({from_date} to {to_date})")
        
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(
                    f"{self.base_url}/data/{symbol}",
                    params={"timeframe": timeframe, "limit": 10000}, # Assume large enough for now, or paginated
                    timeout=30.0
                )
            
            if res.status_code == 200:
                data = res.json()
                if not data: return None
                
                df = pd.DataFrame(data)
                
                # Assume standard GAS format
                if 'time' in df.columns:
                    df['time'] = pd.to_datetime(df['time'], unit='s')
                    df = df[(df['time'] >= from_date) & (df['time'] <= to_date)]
                    df = df.sort_values(by='time')
                    return df
            else:
                 logger.error(f"Market data returned {res.status_code}")
                 return None
        except Exception as e:
            logger.error(f"Failed to fetch market data: {e}")
            return None

market_client = MarketDataClient()
