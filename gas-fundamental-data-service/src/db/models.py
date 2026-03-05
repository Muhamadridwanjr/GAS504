"""SQLAlchemy models for fundamental data."""
from sqlalchemy import Column, Integer, Float, String, BigInteger, DateTime, Index, func
from src.db.database import Base

class FundamentalData(Base):
    __tablename__ = "fundamental_data"
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    indicator = Column(String(100), nullable=False, index=True)
    time = Column(BigInteger, nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(50), default="")
    source = Column(String(100), default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (Index("ix_symbol_indicator_time", "symbol", "indicator", "time", unique=True),)
