import sys
import asyncio
import time
from datetime import datetime
from typing import List, Optional
try:
    import MetaTrader5 as mt5
except ImportError:
    pass  # We only need this if running on Windows in local mode

from src.models.messages import TickMessage, OhlcMessage
from src.processor.forwarder import forwarder
from src.config import settings
from src.lib.logger import log

class LocalMT5Connector:
    def __init__(self):
        self.symbols = settings.SYMBOLS
        self.timeframes = settings.TIMEFRAMES
        self._running = False
        
        # We only really test Windows for local mode, log warning if unsupported
        if sys.platform != "win32":
            log.warning("Local MT5 mode is only fully supported on Windows with the MetaTrader5 package.")
    
    async def start(self):
        log.info(f"Starting Local MT5 Connector for symbols: {self.symbols}")
        
        if 'MetaTrader5' not in sys.modules:
            log.error("MetaTrader5 python package is not installed or available on this OS.")
            return

        if not mt5.initialize(path=settings.MT5_PATH):
            log.error(f"MT5 Initialize failed, error code: {mt5.last_error()}")
            return
            
        log.info("MT5 initialized successfully")
        
        # Subscribe symbols
        for symbol in self.symbols:
            selected = mt5.symbol_select(symbol, True)
            if not selected:
                log.error(f"Failed to select symbol {symbol}")
            else:
                log.info(f"Subscribed to symbol {symbol}")

        self._running = True
        
        try:
            # Main polling loop
            # Note: A pure async event-driven approach with MT5 Python is hard since it blocks.
            # We will use asyncio.sleep to yield control.
            
            last_ohlc_check = time.time()
            
            while self._running:
                # 1. Check Ticks
                for symbol in self.symbols:
                    tick = mt5.symbol_info_tick(symbol)
                    if tick:
                        tick_msg = TickMessage(
                            symbol=symbol,
                            time=tick.time,
                            bid=tick.bid,
                            ask=tick.ask,
                            volume=float(tick.volume)
                        )
                        await forwarder.forward_tick(tick_msg)
                        
                # 2. Check OHLC (every minute roughly)
                current_time = time.time()
                if current_time - last_ohlc_check >= 60:
                    last_ohlc_check = current_time
                    await self._check_ohlc()
                    
                await asyncio.sleep(0.5) # Yield and prevent 100% CPU
                
        except Exception as e:
            log.error(f"Error in Local MT5 Connector loop: {e}")
        finally:
            self.stop()
            
    async def _check_ohlc(self):
        """Fetches recent OHLC candles (simplistic representation)"""
        if 'MetaTrader5' not in sys.modules:
            return
            
        for symbol in self.symbols:
            for tf_str in self.timeframes:
                mt5_tf = self._map_timeframe(tf_str)
                if not mt5_tf:
                    continue
                    
                # Get the last completed candle (index 1)
                rates = mt5.copy_rates_from_pos(symbol, mt5_tf, 1, 1)
                if rates is not None and len(rates) > 0:
                    rate = rates[0]
                    ohlc = OhlcMessage(
                        symbol=symbol,
                        timeframe=tf_str,
                        time=rate['time'],
                        open=rate['open'],
                        high=rate['high'],
                        low=rate['low'],
                        close=rate['close'],
                        volume=float(rate['tick_volume'])
                    )
                    await forwarder.forward_ohlc(ohlc)

    def _map_timeframe(self, tf_str: str) -> Optional[int]:
        if 'MetaTrader5' not in sys.modules:
            return None
        mapping = {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "H1": mt5.TIMEFRAME_H1,
            "D1": mt5.TIMEFRAME_D1,
        }
        return mapping.get(tf_str.upper())

    def stop(self):
        log.info("Stopping Local MT5 Connector")
        self._running = False
        if 'MetaTrader5' in sys.modules:
            mt5.shutdown()
