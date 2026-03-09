import httpx
from typing import List, Dict, Any, Optional
import time

from src.config import settings
from src.lib.logger import logger
from src.core.exceptions import MT5ConnectionError, DataFetchError
from src.lib.utils import timeframe_to_seconds

class MT5Connector:
    def __init__(self):
        self.mode = settings.MT5_MODE
        self.ea_url = f"http://{settings.MT5_EA_HOST}:{settings.MT5_EA_PORT}"
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def fetch_history(self, symbol: str, timeframe: str, from_time: Optional[int] = None, to_time: Optional[int] = None, count: Optional[int] = None) -> List[Dict[str, Any]]:
        if self.mode == "socket":
            return await self._fetch_history_ea(symbol, timeframe, from_time, to_time, count)
        else:
            return await self._fetch_history_local(symbol, timeframe, from_time, to_time, count)

    async def _fetch_history_ea(self, symbol: str, timeframe: str, from_time: Optional[int] = None, to_time: Optional[int] = None, count: Optional[int] = None) -> List[Dict[str, Any]]:
        # This calls the MT5 EA Bridge or another intermediary service providing the actual MT5 connection
        try:
            params = {
                "symbol": symbol,
                "timeframe": timeframe
            }
            if from_time:
                params["from"] = from_time
            if to_time:
                params["to"] = to_time
            if count:
                params["count"] = count

            # In this mocked implementation we simulate returning some dummy data, 
            # as a real MT5 EA connection depends on their specific bridge setup.
            # You would replace this with: 
            # response = await self.client.get(f"{self.ea_url}/history", params=params)
            # return response.json().get("data", [])
            
            logger.info(f"Mock fetching from EA for {symbol} {timeframe}")
            return self._generate_mock_data(symbol, timeframe, from_time, to_time, count)
            
        except Exception as e:
            logger.error(f"Error fetching from EA: {e}")
            raise MT5ConnectionError(f"Failed to connect to MT5 EA: {e}")

    async def _fetch_history_local(self, symbol: str, timeframe: str, from_time: Optional[int] = None, to_time: Optional[int] = None, count: Optional[int] = None) -> List[Dict[str, Any]]:
        try:
            import MetaTrader5 as mt5
            import pandas as pd
            
            if not mt5.initialize():
                logger.error(f"initialize() failed, error code = {mt5.last_error()}")
                raise MT5ConnectionError("Could not initialize MT5")

            tf_map = {
                "M1": mt5.TIMEFRAME_M1,
                "M5": mt5.TIMEFRAME_M5,
                "M15": mt5.TIMEFRAME_M15,
                "M30": mt5.TIMEFRAME_M30,
                "H1": mt5.TIMEFRAME_H1,
                "H4": mt5.TIMEFRAME_H4,
                "D1": mt5.TIMEFRAME_D1,
                "W1": mt5.TIMEFRAME_W1,
                "MN": mt5.TIMEFRAME_MN1,
            }

            mt5_tf = tf_map.get(timeframe)
            if mt5_tf is None:
                raise DataFetchError(f"Unsupported timeframe: {timeframe}")

            if from_time:
                # copy_rates_range(symbol, timeframe, date_from, date_to)
                # date_to defaults to current time if not provided
                to_t = to_time if to_time else int(time.time())
                rates = mt5.copy_rates_range(symbol, mt5_tf, from_time, to_t)
            elif count:
                # copy_rates_from_pos(symbol, timeframe, start_pos, count)
                rates = mt5.copy_rates_from_pos(symbol, mt5_tf, 0, count)
            else:
                rates = mt5.copy_rates_from_pos(symbol, mt5_tf, 0, 100)

            if rates is None or len(rates) == 0:
                logger.warning(f"No data found for {symbol} {timeframe}")
                return []

            df = pd.DataFrame(rates)
            # Convert time to int (seconds)
            df['time'] = df['time'].astype(int)
            
            # Format to list of dicts
            result = df.to_dict(orient="records")
            return result
        except ImportError:
            logger.error("MetaTrader5 or pandas library not found")
            raise MT5ConnectionError("MT5 library or pandas not installed")
        except Exception as e:
            logger.error(f"Error fetching local MT5 history: {e}")
            raise DataFetchError(f"Failed to fetch local history: {e}")

    def _generate_mock_data(self, symbol: str, timeframe: str, from_time: Optional[int] = None, to_time: Optional[int] = None, count: Optional[int] = None) -> List[Dict[str, Any]]:
        """Fallback mock data generation for testing"""
        data = []
        now = int(time.time())
        tf_sec = timeframe_to_seconds(timeframe)
        
        c = count if count else 100
        start_time = now - (c * tf_sec)
        if from_time:
            start_time = from_time
            
        current_time = start_time
        for i in range(c):
            data.append({
                "time": current_time,
                "open": 2000.00 + i,
                "high": 2005.00 + i,
                "low": 1995.00 + i,
                "close": 2002.00 + i,
                "volume": 1234 + i
            })
            current_time += tf_sec
        return data
