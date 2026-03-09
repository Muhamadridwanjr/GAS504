from src.api.models import RiskEvaluateRequest, RiskEvaluateResponse
from src.core.sizer import PositionSizer
from src.config import settings
from src.lib.logger import get_logger

logger = get_logger(__name__)

class RiskEvaluator:
    def __init__(self):
        self.sizer = PositionSizer()

    async def evaluate(self, request: RiskEvaluateRequest) -> RiskEvaluateResponse:
        logger.info(f"Evaluating Risk for account: {request.account_id} | symbol: {request.symbol}")

        # Rule 1: Check Daily Drawdown limit
        if request.current_drawdown >= settings.MAX_DAILY_DRAWDOWN:
            return RiskEvaluateResponse(
                approved=False,
                lot_size=0.0,
                adjusted_sl=0.0,
                adjusted_tp=0.0,
                reason=f"Account drawdown {request.current_drawdown}% exceeds daily limit {settings.MAX_DAILY_DRAWDOWN}%",
                risk_amount=0.0
            )

        # Base mock calculation for SL and TP if not provided from upstream
        # Usually SL/TP distance depends on volatility (ATR). Since we lack feature connection in this mock, 
        # we will use static % distances based on price.
        # Assume 1% SL and 3% TP distances based on signal
        
        sl_pct = 0.01
        tp_pct = 0.03
        
        if request.signal.upper() == "BUY":
            sl_price = request.entry_price * (1 - sl_pct)
            tp_price = request.entry_price * (1 + tp_pct)
        else: # SELL
            sl_price = request.entry_price * (1 + sl_pct)
            tp_price = request.entry_price * (1 - tp_pct)
            
        sl_price = round(sl_price, 3)
        tp_price = round(tp_price, 3)

        # Rule 2: Dynamic Lot Sizing
        # We limit the risk parameter to either the confidence or max risk
        risk_percentage = min(settings.MAX_RISK_PER_TRADE, request.confidence * settings.MAX_RISK_PER_TRADE)
        
        size_data = self.sizer.calculate_lot_size(
            balance=request.account_balance,
            risk_percentage=risk_percentage,
            entry_price=request.entry_price,
            sl_price=sl_price
        )

        return RiskEvaluateResponse(
            approved=True,
            lot_size=size_data["lot_size"],
            adjusted_sl=sl_price,
            adjusted_tp=tp_price,
            reason="Risk parameters within acceptable limits",
            risk_amount=size_data["risk_amount"]
        )
