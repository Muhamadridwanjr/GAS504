"""SQLAlchemy models for fundamental data."""
from sqlalchemy import Column, Integer, Float, String, BigInteger, DateTime, Text, Index, func
from src.db.database import Base


class FundamentalData(Base):
    __tablename__ = "fundamental_data"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    symbol     = Column(String(20), nullable=False, index=True)
    indicator  = Column(String(100), nullable=False, index=True)
    time       = Column(BigInteger, nullable=False)
    value      = Column(Float, nullable=False)
    unit       = Column(String(50), default="")
    source     = Column(String(100), default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (Index("ix_symbol_indicator_time", "symbol", "indicator", "time", unique=True),)


class MacroAnalysis(Base):
    """Stores the AI macro analysis result produced after each scrape cycle."""
    __tablename__ = "macro_analysis"
    id                  = Column(Integer, primary_key=True, autoincrement=True)
    generated_at        = Column(DateTime(timezone=True), nullable=False, index=True)
    market_regime       = Column(String(50))        # RISK_ON / RISK_OFF / MIXED / STAGFLATION_RISK
    overall_risk        = Column(String(20))        # LOW / MODERATE / HIGH
    growth_pressure     = Column(Integer, default=0)
    inflation_pressure  = Column(Integer, default=0)
    narrative           = Column(Text)
    currency_scores_json = Column(Text)             # JSON blob: {USD: {score,bias}, ...}
    indicators_analyzed = Column(Integer, default=0)
    created_at          = Column(DateTime(timezone=True), server_default=func.now())
