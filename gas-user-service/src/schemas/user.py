from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, List, Any
from uuid import UUID
from datetime import datetime, date

class UserProfileBase(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    settings: Dict[str, Any] = {}

class UserProfileCreate(UserProfileBase):
    supabase_user_id: UUID
    email: EmailStr

class UserProfileUpdate(UserProfileBase):
    pass

class UserProfileResponse(UserProfileBase):
    id: UUID
    supabase_user_id: UUID
    email: str
    subscription_tier: str
    daily_request_count: int
    last_request_date: Optional[date] = None
    referral_code: Optional[str] = None
    referred_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class InternalProfileCreate(BaseModel):
    supabase_user_id: UUID
    email: EmailStr

class InternalTierUpdate(BaseModel):
    tier: str

class APIKeyCreate(BaseModel):
    name: str

class VerifyAPIKeyRequest(BaseModel):
    api_key: str
