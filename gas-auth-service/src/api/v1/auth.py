import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import bcrypt as _bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from urllib.parse import urlencode, quote
from typing import Optional

from src.config import settings
from src.core.database import get_db
from src.core.auth_handler import auth_handler
from src.models.user import User
from src.utils.logger import logger

def hash_password(plain: str) -> str:
    return _bcrypt.hashpw(plain.encode(), _bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return _bcrypt.checkpw(plain.encode(), hashed.encode())

router = APIRouter()

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def get_token(authorization: Optional[str] = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    return authorization.split(" ")[1]


class LoginRequest(BaseModel):
    username: str   # accepts username OR email
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = ""


@router.post("/register")
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check username/email unique
    result = await db.execute(
        select(User).where(or_(User.username == data.username, User.email == data.email))
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Username atau email sudah terdaftar")

    user = User(
        username=data.username,
        email=data.email,
        full_name=data.full_name,
        password_hash=hash_password(data.password),
        role="user",
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    jwt_token = auth_handler.create_token(user.id, user.email)
    logger.info("user_registered", username=user.username)
    return {
        "access_token": jwt_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "avatar_url": user.avatar_url,
        }
    }


@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(or_(User.username == data.username, User.email == data.username))
    )
    user = result.scalar_one_or_none()

    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    jwt_token = auth_handler.create_token(user.id, user.email or user.username)
    logger.info("user_login", username=user.username)
    return {
        "access_token": jwt_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "avatar_url": user.avatar_url,
        }
    }


@router.get("/google")
async def google_login():
    """Return Google OAuth URL for frontend to redirect to."""
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
    }
    url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return {"url": url}


@router.get("/google/callback")
async def google_callback(code: str, db: AsyncSession = Depends(get_db)):
    """Handle Google OAuth callback, upsert user, issue JWT, redirect to frontend."""
    async with httpx.AsyncClient() as client:
        # Exchange code for access token
        token_res = await client.post(GOOGLE_TOKEN_URL, data={
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        })
        if token_res.status_code != 200:
            logger.error("google_token_exchange_failed", response=token_res.text)
            raise HTTPException(status_code=400, detail="Failed to exchange code with Google")

        google_tokens = token_res.json()

        # Get user info from Google
        userinfo_res = await client.get(GOOGLE_USERINFO_URL, headers={
            "Authorization": f"Bearer {google_tokens['access_token']}"
        })
        if userinfo_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user info from Google")

        google_user = userinfo_res.json()

    # Upsert user in local DB
    result = await db.execute(select(User).where(User.google_id == google_user["sub"]))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            google_id=google_user["sub"],
            email=google_user["email"],
            full_name=google_user.get("name", ""),
            avatar_url=google_user.get("picture", ""),
        )
        db.add(user)
        logger.info("user_created", email=user.email)
    else:
        user.full_name = google_user.get("name", user.full_name)
        user.avatar_url = google_user.get("picture", user.avatar_url)
        logger.info("user_logged_in", email=user.email)

    await db.commit()
    await db.refresh(user)

    # Issue local JWT
    jwt_token = auth_handler.create_token(user.id, user.email)

    # Redirect to frontend with token in query params
    redirect_url = (
        f"{settings.FRONTEND_URL}/auth/callback"
        f"?token={jwt_token}"
        f"&email={quote(user.email)}"
        f"&name={quote(user.full_name or '')}"
        f"&avatar={quote(user.avatar_url or '')}"
    )
    return RedirectResponse(url=redirect_url)


class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None


@router.patch("/profile")
async def update_profile(data: ProfileUpdateRequest, token: str = Depends(get_token), db: AsyncSession = Depends(get_db)):
    payload = auth_handler.verify_token(token)
    result = await db.execute(select(User).where(User.id == payload["sub"]))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if data.full_name is not None:
        user.full_name = data.full_name
    if data.email is not None:
        user.email = data.email
    await db.commit()
    await db.refresh(user)
    return {"id": user.id, "username": user.username, "full_name": user.full_name, "email": user.email, "role": user.role, "avatar_url": user.avatar_url}


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


@router.post("/change-password")
async def change_password(data: ChangePasswordRequest, token: str = Depends(get_token), db: AsyncSession = Depends(get_db)):
    payload = auth_handler.verify_token(token)
    result = await db.execute(select(User).where(User.id == payload["sub"]))
    user = result.scalar_one_or_none()
    if not user or not user.password_hash:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(data.old_password, user.password_hash):
        raise HTTPException(status_code=401, detail="Password lama salah")
    if len(data.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password minimal 8 karakter")
    user.password_hash = hash_password(data.new_password)
    await db.commit()
    return {"status": "ok", "message": "Password berhasil diubah"}


@router.post("/verify")
async def verify(token: str = Depends(get_token)):
    payload = auth_handler.verify_token(token)
    return {"valid": True, "payload": payload}


@router.get("/user")
async def get_user(token: str = Depends(get_token), db: AsyncSession = Depends(get_db)):
    payload = auth_handler.verify_token(token)
    result = await db.execute(select(User).where(User.id == payload["sub"]))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "avatar_url": user.avatar_url,
    }
