"""
GAS Auth Admin — Internal user listing endpoint.
Called by gas-web-backend admin API. Protected by internal API key.
"""
import os
from fastapi import APIRouter, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import Depends
from src.core.database import get_db
from src.models.user import User

router = APIRouter()

INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "gas-internal-key-2026")


def _check_key(x_internal_key: str = Header(default="", alias="X-Internal-Key")):
    if x_internal_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Internal API key invalid")


@router.get("/admin/users")
async def list_users(
    skip: int = 0,
    limit: int = 100,
    search: str = "",
    _=Depends(_check_key),
    db: AsyncSession = Depends(get_db),
):
    """List all registered users (internal use by web-backend admin)."""
    q = select(User)
    if search:
        q = q.where(
            (User.username.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%")) |
            (User.full_name.ilike(f"%{search}%"))
        )
    q = q.order_by(User.id.desc()).offset(skip).limit(limit)
    result = await db.execute(q)
    users = result.scalars().all()

    # Total count
    count_q = select(func.count()).select_from(User)
    if search:
        count_q = count_q.where(
            (User.username.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%")) |
            (User.full_name.ilike(f"%{search}%"))
        )
    total_res = await db.execute(count_q)
    total = total_res.scalar_one()

    return {
        "users": [
            {
                "id": str(u.id),
                "username": u.username or "",
                "email": u.email or "",
                "full_name": u.full_name or "",
                "role": u.role or "user",
                "is_active": u.is_active,
                "avatar_url": u.avatar_url or "",
                "google_id": u.google_id or "",
            }
            for u in users
        ],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/admin/users/{user_id}")
async def get_user_by_id(
    user_id: str,
    _=Depends(_check_key),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": str(user.id),
        "username": user.username or "",
        "email": user.email or "",
        "full_name": user.full_name or "",
        "role": user.role or "user",
        "is_active": user.is_active,
        "avatar_url": user.avatar_url or "",
    }


@router.patch("/admin/users/{user_id}/toggle-active")
async def toggle_user_active(
    user_id: str,
    _=Depends(_check_key),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = not user.is_active
    await db.commit()
    return {"id": str(user.id), "is_active": user.is_active}
