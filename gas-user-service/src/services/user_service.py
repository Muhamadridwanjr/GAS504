from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from src.models.user import UserProfile
from src.schemas.user import UserProfileCreate, UserProfileUpdate
from uuid import UUID
from src.utils.logger import logger

class UserService:
    @staticmethod
    async def get_profile_by_supabase_id(db: AsyncSession, supabase_user_id: UUID):
        result = await db.execute(
            select(UserProfile).where(UserProfile.supabase_user_id == supabase_user_id)
        )
        return result.scalars().first()

    @staticmethod
    async def create_profile(db: AsyncSession, profile_in: UserProfileCreate):
        db_profile = UserProfile(**profile_in.dict())
        db.add(db_profile)
        await db.commit()
        await db.refresh(db_profile)
        return db_profile

    @staticmethod
    async def update_profile(db: AsyncSession, supabase_user_id: UUID, profile_in: UserProfileUpdate):
        await db.execute(
            update(UserProfile)
            .where(UserProfile.supabase_user_id == supabase_user_id)
            .values(**profile_in.dict(exclude_unset=True))
        )
        await db.commit()
        return await UserService.get_profile_by_supabase_id(db, supabase_user_id)

    @staticmethod
    async def update_tier(db: AsyncSession, supabase_user_id: UUID, tier: str):
        await db.execute(
            update(UserProfile)
            .where(UserProfile.supabase_user_id == supabase_user_id)
            .values(subscription_tier=tier)
        )
        await db.commit()
        return await UserService.get_profile_by_supabase_id(db, supabase_user_id)
