import uuid
from typing import Dict, Any
from src.api.models import BacktestRequest, BacktestResponse, SummaryStats
from src.data.market_data_client import market_client
from src.core.simulator import Simulator
from src.core.metrics import calculate_metrics
from src.lib.logger import logger

class BacktestEngine:
    async def run_backtest(self, req: BacktestRequest) -> BacktestResponse:
        logger.info(f"Running backtest for {req.symbol} from {req.from_date} to {req.to_date}")
        
        bt_id = f"bt_{uuid.uuid4().hex[:8]}"
        
        # 1. Fetch Data
        df = await market_client.get_historical_data(req.symbol, req.timeframe, req.from_date, req.to_date)
        
        if df is None or df.empty:
            logger.error("No historical data found for backtest.")
            raise ValueError("No historical data available for the specified range.")
            
        # 2. Setup Simulator
        sim = Simulator(
            initial_capital=req.initial_capital,
            commission=req.commission,
            slippage=req.slippage
        )
        
        # 3. Execute
        trades, eq_curve = sim.execute(df, req.strategy)
        
        # 4. Calculate Metrics
        metrics = calculate_metrics(trades, eq_curve, req.initial_capital)
        
        # 5. Build Response
        response = BacktestResponse(
            backtest_id=bt_id,
            status="completed",
            summary=SummaryStats(**metrics),
            equity_curve=eq_curve,
            trades=trades
        )
        
        # 6. Save if requested (Omitted full DB write in this stub, but would go here)
        if req.save_result:
            logger.info("Saving results to database...")
            # DB code here
            
        return response

engine = BacktestEngine()
