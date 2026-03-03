from sqlalchemy import Column, String, Float, Integer, JSON, DateTime
from sqlalchemy.sql import func
from src.db.database import Base
import uuid

class BacktestResult(Base):
    __tablename__ = "backtest_results"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(String, default="completed")
    symbol = Column(String, nullable=False)
    timeframe = Column(String, nullable=False)
    
    total_return = Column(Float)
    annualized_return = Column(Float)
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)
    win_rate = Column(Float)
    profit_factor = Column(Float)
    total_trades = Column(Integer)
    
    # Store complex structures as JSON
    strategy_params = Column(JSON)
    equity_curve = Column(JSON)
    trades = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
