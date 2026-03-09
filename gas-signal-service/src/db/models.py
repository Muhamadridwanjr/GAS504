import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Boolean, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from src.db.database import Base
import enum

class SignalTier(str, enum.Enum):
    insider = "insider"
    premium = "premium"
    ultimate = "ultimate"
    
class SignalAction(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"

class Signal(Base):
    __tablename__ = "signals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tier = Column(Enum(SignalTier), nullable=False, index=True)
    source = Column(String, nullable=False, index=True)
    symbol = Column(String, nullable=False, index=True)
    timeframe = Column(String, nullable=True)
    action = Column(Enum(SignalAction), nullable=False)
    entry_price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    take_profit = Column(Float, nullable=False)
    confidence = Column(Float, nullable=True)
    metadata_info = Column(JSONB, nullable=True) # avoiding 'metadata' keyword clash in SA
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
