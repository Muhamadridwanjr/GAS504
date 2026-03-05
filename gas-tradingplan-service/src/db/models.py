from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Text, func
from src.db.database import Base

class TradingPlan(Base):
    __tablename__ = "trading_plans"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, default="")
    plan_date = Column(Date, nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    direction = Column(String(10), nullable=False)  # BUY or SELL
    entry_price = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    notes = Column(Text, default="")
    status = Column(String(20), default="active", index=True)  # active, completed, canceled
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
