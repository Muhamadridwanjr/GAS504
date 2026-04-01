from sqlalchemy import Column, Integer, String, Float, DateTime, Text, func
from src.db.database import Base


class EconomicEvent(Base):
    __tablename__ = "economic_events"
    id             = Column(Integer, primary_key=True, autoincrement=True)
    provider       = Column(String(50), default="ecocal")
    title          = Column(String(255), nullable=False)
    country        = Column(String(10), nullable=False, index=True)
    importance     = Column(String(20), index=True)
    time_utc       = Column(DateTime(timezone=True), nullable=False, index=True)
    actual_value   = Column(Float, nullable=True)
    forecast_value = Column(Float, nullable=True)
    previous_value = Column(Float, nullable=True)
    unit           = Column(String(50), default="")
    created_at     = Column(DateTime(timezone=True), server_default=func.now())


class News(Base):
    __tablename__ = "news"
    id           = Column(Integer, primary_key=True, autoincrement=True)
    title        = Column(String(500), nullable=False)
    source       = Column(String(100))
    url          = Column(String(1000))
    published_at = Column(DateTime(timezone=True))
    summary      = Column(String(2000))
    created_at   = Column(DateTime(timezone=True), server_default=func.now())


class CalendarAnalysis(Base):
    """Stores daily AI sentiment analysis of the economic calendar."""
    __tablename__ = "calendar_analysis"
    id                       = Column(Integer, primary_key=True, autoincrement=True)
    generated_at             = Column(DateTime(timezone=True), nullable=False, index=True)
    total_events             = Column(Integer, default=0)
    high_volatility_expected = Column(String(5), default="false")  # "true"/"false"
    risk_on_currencies       = Column(String(200))   # comma-separated
    risk_off_currencies      = Column(String(200))   # comma-separated
    currency_sentiment_json  = Column(Text)          # JSON blob per currency
    priority_events_json     = Column(Text)          # JSON list of classified events
    created_at               = Column(DateTime(timezone=True), server_default=func.now())
