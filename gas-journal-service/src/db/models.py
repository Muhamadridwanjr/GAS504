import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Boolean, Enum, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from src.db.database import Base
import enum


class TradeAction(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class TradeStatus(str, enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    CANCELED = "CANCELED"


class AnalysisSignal(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"
    NEUTRAL = "NEUTRAL"


class Trade(Base):
    __tablename__ = "trades"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    symbol = Column(String, nullable=False, index=True)
    action = Column(Enum(TradeAction), nullable=False)
    entry_price = Column(Numeric(precision=18, scale=8), nullable=False)
    exit_price = Column(Numeric(precision=18, scale=8), nullable=True)
    lot = Column(Numeric(precision=12, scale=4), nullable=False)
    profit = Column(Numeric(precision=18, scale=8), nullable=True)
    commission = Column(Numeric(precision=12, scale=4), nullable=True, default=0)
    swap = Column(Numeric(precision=12, scale=4), nullable=True, default=0)
    entry_time = Column(DateTime(timezone=True), nullable=False, index=True)
    exit_time = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(TradeStatus), nullable=False, default=TradeStatus.OPEN, index=True)
    analysis_id = Column(UUID(as_uuid=True), nullable=True)
    metadata_info = Column(JSONB, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class Analysis(Base):
    __tablename__ = "analysis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    symbol = Column(String, nullable=False, index=True)
    timeframe = Column(String, nullable=True)
    signal = Column(Enum(AnalysisSignal), nullable=False)
    entry_price = Column(Numeric(precision=18, scale=8), nullable=True)
    stop_loss = Column(Numeric(precision=18, scale=8), nullable=True)
    take_profit = Column(Numeric(precision=18, scale=8), nullable=True)
    confidence = Column(Float, nullable=True)
    reason = Column(Text, nullable=True)
    metadata_info = Column(JSONB, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
