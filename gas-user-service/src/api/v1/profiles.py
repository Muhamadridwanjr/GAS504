from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.core.dependencies import get_current_user_id, verify_internal_api_key
from src.schemas.user import (
    UserProfileResponse, UserProfileUpdate, 
    InternalProfileCreate, InternalTierUpdate,
    UserProfileCreate
)
from src.services.user_service import UserService
from uuid import UUID
from src.utils.logger import logger

router = APIRouter()

# --- Protected Endpoints (User) ---

@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    profile = await UserService.get_profile_by_supabase_id(db, user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    return profile

@router.put("/me", response_model=UserProfileResponse)
async def update_my_profile(
    profile_in: UserProfileUpdate,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    profile = await UserService.update_profile(db, user_id, profile_in)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    return profile

# --- Internal Endpoints (Service-to-Service) ---

@router.post("/internal/profiles", response_model=UserProfileResponse, dependencies=[Depends(verify_internal_api_key)])
async def create_internal_profile(
    profile_in: InternalProfileCreate,
    db: AsyncSession = Depends(get_db)
):
    # Check if exists
    existing = await UserService.get_profile_by_supabase_id(db, profile_in.supabase_user_id)
    if existing:
        return existing
        
    p_create = UserProfileCreate(**profile_in.dict())
    return await UserService.create_profile(db, p_create)

@router.put("/internal/profiles/{supabase_user_id}/tier", response_model=UserProfileResponse, dependencies=[Depends(verify_internal_api_key)])
async def update_internal_tier(
    supabase_user_id: UUID,
    tier_in: InternalTierUpdate,
    db: AsyncSession = Depends(get_db)
):
    profile = await UserService.update_tier(db, supabase_user_id, tier_in.tier)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    return profile
