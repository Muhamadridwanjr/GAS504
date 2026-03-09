from src.config import settings
from src.lib.logger import get_logger

logger = get_logger(__name__)

class PositionSizer:
    @staticmethod
    def calculate_lot_size(balance: float, risk_percentage: float, entry_price: float, sl_price: float, leverage: float = 100) -> dict:
        """
        Calculate the appropriate lot size based on balance, risk tolerance, and stop loss distance.
        Note: This is a simplified calculation. In a real environment, it would adapt to the instrument's contract size.
        """
        if balance <= 0 or sl_price <= 0 or entry_price <= 0 or entry_price == sl_price:
            return {"lot_size": 0.0, "risk_amount": 0.0, "adjusted_sl": sl_price}

        # Maximum amount the user is willing to lose on this trade
        risk_amount = balance * (risk_percentage / 100.0)
        
        # Absolute distance to stop loss
        sl_distance = abs(entry_price - sl_price)

        # Simplified Lot calculation (e.g., $1 movement per 1 lot)
        # Assuming 1 Standard Lot = 100,000 units. If price moves 1 point (e.g. 1.0000 to 1.0001), 
        # it's usually $10 for standard lot in some EURUSD pairs, but it varies wildly.
        # Here we provide a normalized generic size logic:
        # Risk Amount = Lot Size * Point Value * SL Distance in points
        # Lot Size = Risk Amount / (SL Distance * Point Value)
        # Using a fixed placeholder Point Value = 100 for normalization
        point_value = 100.0 
        calculated_lot = risk_amount / (sl_distance * point_value)
        
        # Round to 2 decimal places (standard broker precision)
        lot_size = round(calculated_lot, 2)
        
        # Enforce limits (example: max 5 lots, min 0.01)
        lot_size = max(0.01, min(lot_size, 5.0))
        
        return {
            "lot_size": lot_size,
            "risk_amount": round(risk_amount, 2),
            "adjusted_sl": sl_price
        }
