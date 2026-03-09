from src.detection.market_structure import MarketStructureDetector
from src.detection.zones import ZonesDetector
from src.detection.liquidity import LiquidityDetector
from src.detection.entry import EntryTriggerDetector
from src.style.manager import StyleManager

class Orchestrator:
    def __init__(self):
        self.market_structure = MarketStructureDetector()
        self.zones = ZonesDetector()
        self.liquidity = LiquidityDetector()
        self.entry = EntryTriggerDetector()
        self.style_manager = StyleManager()

    def analyze(self, request_data: dict) -> dict:
        # Example dummy aggregation logic based on request
        # In a real integration, the engine would parse the OHLC payload
        trading_style = request_data.get("options", {}).get("trading_style", "intraday")
        
        market_structure_res = self.market_structure.detect(request_data["ohlc"], request_data["options"])
        zones_res = self.zones.detect(request_data["ohlc"], request_data["options"])
        liquidity_res = self.liquidity.detect(request_data["ohlc"], request_data["options"])
        entry_res = self.entry.detect(request_data["ohlc"], request_data["options"])
        
        return {
            "symbol": request_data.get("symbol", "UNKNOWN"),
            "trading_style": trading_style,
            "timeframes": request_data.get("timeframes", getattr(request_data.get("options", {}), "timeframes", {})),
            "market_structure": market_structure_res,
            "zones": zones_res,
            "liquidity": liquidity_res,
            "entry": entry_res,
            "signal": {
                "action": "BUY",
                "entry_price": entry_res["ote"]["price"],
                "stop_loss": entry_res["ote"]["price"] - 6.5,
                "take_profit": entry_res["ote"]["price"] + 21.5,
                "confidence": 0.85
            }
        }
