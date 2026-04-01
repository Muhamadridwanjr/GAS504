import os
import jwt
from typing import Optional
from fastapi import Header, HTTPException

JWT_SECRET = os.getenv("JWT_SECRET", "dummy-jwt-secret")
JWT_ALGORITHM = "HS256"

# Admin user IDs cached in-memory (populated on first admin login)
_admin_user_ids: set = set()

ADMIN_ROLES = {"admin"}


async def get_current_user(
    x_user_id: Optional[str] = Header(default=None, alias="X-User-ID"),
    x_user_role: Optional[str] = Header(default=None, alias="X-User-Role"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
) -> str:
    """Return user_id. For admin detection use get_current_user_info."""
    info = await _resolve_user(x_user_id, x_user_role, authorization)
    return info["user_id"]


async def get_current_user_info(
    x_user_id: Optional[str] = Header(default=None, alias="X-User-ID"),
    x_user_role: Optional[str] = Header(default=None, alias="X-User-Role"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
) -> dict:
    """Return dict with user_id and role."""
    return await _resolve_user(x_user_id, x_user_role, authorization)


async def _resolve_user(x_user_id, x_user_role, authorization) -> dict:
    # 1. X-User-ID injected by gateway (trusted internal header)
    if x_user_id:
        role = x_user_role or "user"
        return {"user_id": x_user_id, "role": role, "is_admin": role in ADMIN_ROLES, "username": "", "email": ""}

    # 2. Parse JWT from Authorization: Bearer <token>
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_id = payload.get("sub")
            role = payload.get("role", "user")
            username = payload.get("username", "")
            email = payload.get("email", "")
            if user_id:
                return {"user_id": str(user_id), "role": role, "is_admin": role in ADMIN_ROLES, "username": username, "email": email}
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired. Silakan login ulang.")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Token tidak valid.")

    raise HTTPException(status_code=401, detail="Autentikasi diperlukan. Silakan login.")
