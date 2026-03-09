from sqlalchemy import Column, String, Integer, Date, DateTime, UUID, JSON, ForeignKey
from sqlalchemy.sql import func
from src.core.database import Base
import uuid

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supabase_user_id = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True)
    email = Column(String, nullable=False, index=True)
    full_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    subscription_tier = Column(String, default="free", index=True)
    daily_request_count = Column(Integer, default=0)
    last_request_date = Column(Date, nullable=True)
    settings = Column(JSON, default={})
    api_keys = Column(JSON, default=[])
    referral_code = Column(String, unique=True, nullable=True)
    referred_by = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
