from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, UUID
from sqlalchemy.orm import relationship
from src.core.database import Base
import uuid
from datetime import datetime

class UserCredits(Base):
    __tablename__ = "user_credits"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tier = Column(String, default="free")  # essential, plus, premium, ultimate, free
    quota = Column(Integer, default=0)
    boost = Column(Integer, default=0)
    daily_usage = Column(Integer, default=0)
    last_reset_date = Column(DateTime, default=datetime.utcnow)
    level_score = Column(Integer, default=0)
    level = Column(Integer, default=1)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_credits.user_id"), nullable=False)
    tier = Column(String, nullable=False)
    status = Column(String, default="active")  # active, cancelled, expired
    billing_cycle = Column(String, default="monthly") # monthly, annual
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    
    user = relationship("UserCredits", backref="subscriptions")

class AnalysisUsage(Base):
    __tablename__ = "analysis_usage"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    type = Column(String)  # technical / fundamental / hybrid
    status = Column(String) # success / failed
    credit_type = Column(String) # quota / boost
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(JSON, nullable=True)
