from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class Rule(BaseModel):
    indicator: str
    operator: str
    value: float
    action: str

class StrategyConfig(BaseModel):
    type: str = "rule_based"
    rules: List[Rule]
    position_size: float = 0.1
    stop_loss: float = 50.0
    take_profit: float = 100.0

class BacktestRequest(BaseModel):
    strategy: StrategyConfig
    symbol: str
    timeframe: str = "H1"
    from_date: str
    to_date: str
    initial_capital: float = 10000.0
    commission: float = 0.001
    slippage: float = 0.0001
    save_result: bool = False

class SummaryStats(BaseModel):
    total_return: float
    annualized_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int

class BacktestResponse(BaseModel):
    backtest_id: str
    status: str
    summary: SummaryStats
    equity_curve: List[Dict[str, float]]
    trades: List[Dict[str, Any]]
