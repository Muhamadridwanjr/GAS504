"""
Run this script to create initial admin users.
Usage (from gas-auth-service dir):
    python -m scripts.seed_users
Or inside Docker:
    docker exec -it gas-auth-service python -m scripts.seed_users
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bcrypt as _bcrypt
from sqlalchemy import select
from src.core.database import AsyncSessionLocal, engine, Base
from src.models.user import User


def hash_password(plain: str) -> str:
    return _bcrypt.hashpw(plain.encode(), _bcrypt.gensalt()).decode()

USERS = [
    {
        "username": "admin1234",
        "full_name": "admin1234",
        "password": "admin1234gas2026",
        "role": "admin",
        "email": "admin1234@gas.local",
    },
    {
        "username": "ridwanjr",
        "full_name": "ridwanjr",
        "password": "a4z2026dc",
        "role": "admin",
        "email": "ridwanjr@gas.local",
    },
]


async def seed():
    # Ensure tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        for u in USERS:
            result = await db.execute(select(User).where(User.username == u["username"]))
            existing = result.scalar_one_or_none()

            if existing:
                print(f"[SKIP] User '{u['username']}' already exists.")
                continue

            user = User(
                username=u["username"],
                full_name=u["full_name"],
                email=u["email"],
                password_hash=hash_password(u["password"]),
                role=u["role"],
                is_active=True,
            )
            db.add(user)
            print(f"[CREATE] User '{u['username']}' created (role={u['role']})")

        await db.commit()
        print("Done.")


if __name__ == "__main__":
    asyncio.run(seed())
