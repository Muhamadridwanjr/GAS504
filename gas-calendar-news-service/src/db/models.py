from sqlalchemy import Column, Integer, String, BigInteger, Float, DateTime, func
from src.db.database import Base

class EconomicEvent(Base):
    __tablename__ = "economic_events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    provider = Column(String(50), default="forex_factory")
    title = Column(String(255), nullable=False)
    country = Column(String(10), nullable=False, index=True)
    importance = Column(String(20), index=True)
    time_utc = Column(DateTime(timezone=True), nullable=False, index=True)
    actual_value = Column(Float, nullable=True)
    forecast_value = Column(Float, nullable=True)
    previous_value = Column(Float, nullable=True)
    unit = Column(String(50), default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    source = Column(String(100))
    url = Column(String(1000))
    published_at = Column(DateTime(timezone=True))
    summary = Column(String(2000))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
