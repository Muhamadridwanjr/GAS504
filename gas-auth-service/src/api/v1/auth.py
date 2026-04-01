import asyncio
import httpx
import os
import random
import shutil
import string
import time
from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Request, status, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import bcrypt as _bcrypt
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from urllib.parse import urlencode, quote
from typing import Optional

from src.config import settings
from src.core.database import get_db
from src.core.auth_handler import auth_handler
from src.models.user import User
from src.utils.logger import logger
from src.utils.email import send_welcome_email, send_otp_email

REDIS_URL = os.getenv("REDIS_URL", "redis://gas-redis:6379/0")
OTP_TTL   = 600  # 10 minutes
_redis_client: Optional[aioredis.Redis] = None

async def _get_redis() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis_client

def _gen_otp() -> str:
    return "".join(random.choices(string.digits, k=6))

def hash_password(plain: str) -> str:
    return _bcrypt.hashpw(plain.encode(), _bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return _bcrypt.checkpw(plain.encode(), hashed.encode())

router = APIRouter()

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

# Admin usernames — always get role="admin" and full feature access
ADMIN_USERNAMES = {"admin", "ridwanjr"}


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


class SendOtpRequest(BaseModel):
    email: str
    username: Optional[str] = ""  # used in email greeting

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = ""
    otp: str  # OTP code from email verification


@router.post("/send-otp")
async def send_otp(data: SendOtpRequest, background_tasks: BackgroundTasks):
    """Send 6-digit OTP to user's email. Rate-limited: 1 request per 60s per email."""
    email = data.email.strip().lower()
    r = await _get_redis()

    # Rate limit: 1 OTP per 60s
    rate_key = f"otp:rate:{email}"
    if await r.get(rate_key):
        raise HTTPException(status_code=429, detail="Tunggu 60 detik sebelum kirim OTP lagi.")

    otp = _gen_otp()
    otp_key = f"otp:verify:{email}"

    # Store OTP in Redis with 10min TTL
    await r.set(otp_key, otp, ex=OTP_TTL)
    # Rate limit key: 60s TTL
    await r.set(rate_key, "1", ex=60)

    # Send OTP email in background
    background_tasks.add_task(send_otp_email, email, otp, data.username or email.split("@")[0])

    logger.info("otp_sent", email=email)
    return {"status": "ok", "message": f"Kode OTP dikirim ke {email}. Berlaku 10 menit."}


IP_REG_LIMIT = 10  # max accounts per IP

@router.post("/register")
async def register(data: RegisterRequest, request: Request, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    # Verify OTP first
    r = await _get_redis()
    otp_key = f"otp:verify:{data.email.strip().lower()}"
    stored_otp = await r.get(otp_key)
    if not stored_otp:
        raise HTTPException(status_code=400, detail="Kode OTP tidak ditemukan atau sudah kadaluarsa. Kirim ulang OTP.")
    if stored_otp != data.otp.strip():
        raise HTTPException(status_code=400, detail="Kode OTP salah. Periksa email kamu.")

    # OTP valid — delete it immediately (one-time use)
    await r.delete(otp_key)

    # ── IP Registration limit (max 10 accounts per IP) ────────────────────────
    client_ip = (
        request.headers.get("X-Real-IP")
        or request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        or (request.client.host if request.client else "unknown")
    )
    ip_key = f"reg:ip:{client_ip}"
    ip_count = int(await r.get(ip_key) or 0)
    if ip_count >= IP_REG_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Batas pendaftaran akun dari IP ini tercapai (maks {IP_REG_LIMIT} akun). Hubungi support."
        )

    # Check username/email unique
    result = await db.execute(
        select(User).where(or_(User.username == data.username, User.email == data.email))
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Username atau email sudah terdaftar")

    # Auto-assign admin role for designated admin accounts
    assigned_role = "admin" if data.username.lower() in ADMIN_USERNAMES else "user"

    user = User(
        username=data.username,
        email=data.email,
        full_name=data.full_name,
        password_hash=hash_password(data.password),
        role=assigned_role,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    jwt_token = auth_handler.create_token(user.id, user.email, role=user.role, username=user.username or "")
    logger.info("user_registered", username=user.username)

    # ── Set trial plan + credits in Redis ─────────────────────────────────────
    user_id = str(user.id)
    TRIAL_DAYS = 3
    trial_expires_ts = int(time.time()) + (TRIAL_DAYS * 86400)
    trial_expires_dt = __import__("datetime").datetime.utcfromtimestamp(trial_expires_ts).strftime("%Y-%m-%d %H:%M UTC")

    if assigned_role == "admin":
        await r.set(f"user:{user_id}:credits", "999999")
        await r.set(f"user:{user_id}:plan", "ultimate")
    else:
        await r.set(f"user:{user_id}:credits", "10")
        await r.set(f"user:{user_id}:plan", "trial", ex=TRIAL_DAYS * 86400)
        await r.set(f"user:{user_id}:trial_expires_at", str(trial_expires_ts), ex=TRIAL_DAYS * 86400)
        await r.set(f"user:{user_id}:trial_expires_dt", trial_expires_dt, ex=TRIAL_DAYS * 86400)

    # ── Increment IP counter ──────────────────────────────────────────────────
    await r.incr(ip_key)
    await r.expire(ip_key, 365 * 86400)  # keep for 1 year

    # Send welcome email in background (non-blocking)
    if user.email:
        background_tasks.add_task(
            send_welcome_email,
            user.email,
            user.username,
            user.full_name or "",
        )

    return {
        "access_token": jwt_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "plan": "ultimate" if assigned_role == "admin" else "trial",
            "avatar_url": user.avatar_url,
            "is_admin": assigned_role == "admin",
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

    # Sync admin role for designated admin accounts (handles existing users)
    if user.username and user.username.lower() in ADMIN_USERNAMES and user.role != "admin":
        user.role = "admin"
        await db.commit()
        await db.refresh(user)

    jwt_token = auth_handler.create_token(user.id, user.email or user.username, role=user.role, username=user.username or "")
    logger.info("user_login", username=user.username)

    # Read actual plan from Redis (may be trial/free/essential/plus/premium/ultimate/ultra)
    _r = await _get_redis()
    _uid = str(user.id)
    if user.role == "admin":
        _plan = "ultimate"
    else:
        _plan = (await _r.get(f"user:{_uid}:plan")) or "free"
        # Check trial expiry
        if _plan == "trial":
            _trial_exp = int((await _r.get(f"user:{_uid}:trial_expires_at")) or 0)
            if _trial_exp and time.time() > _trial_exp:
                await _r.set(f"user:{_uid}:plan", "free")
                _plan = "free"

    return {
        "access_token": jwt_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "plan": _plan,
            "avatar_url": user.avatar_url,
            "is_admin": user.role == "admin",
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

    is_new_user = False
    if not user:
        user = User(
            google_id=google_user["sub"],
            email=google_user["email"],
            full_name=google_user.get("name", ""),
            avatar_url=google_user.get("picture", ""),
        )
        db.add(user)
        is_new_user = True
        logger.info("user_created", email=user.email)
    else:
        user.full_name = google_user.get("name", user.full_name)
        user.avatar_url = google_user.get("picture", user.avatar_url)
        logger.info("user_logged_in", email=user.email)

    await db.commit()
    await db.refresh(user)

    # Set trial for new Google OAuth users
    if is_new_user:
        _r = await _get_redis()
        _uid = str(user.id)
        _TRIAL_DAYS = 3
        _trial_ts = int(time.time()) + (_TRIAL_DAYS * 86400)
        _trial_dt = __import__("datetime").datetime.utcfromtimestamp(_trial_ts).strftime("%Y-%m-%d %H:%M UTC")
        if user.role == "admin":
            await _r.set(f"user:{_uid}:credits", "999999")
            await _r.set(f"user:{_uid}:plan", "ultimate")
        else:
            await _r.set(f"user:{_uid}:credits", "10")
            await _r.set(f"user:{_uid}:plan", "trial", ex=_TRIAL_DAYS * 86400)
            await _r.set(f"user:{_uid}:trial_expires_at", str(_trial_ts), ex=_TRIAL_DAYS * 86400)
            await _r.set(f"user:{_uid}:trial_expires_dt", _trial_dt, ex=_TRIAL_DAYS * 86400)

    # Send welcome email to new Google OAuth users (fire-and-forget)
    if is_new_user and user.email:
        asyncio.create_task(asyncio.to_thread(
            send_welcome_email, user.email,
            user.username or user.email.split("@")[0],
            user.full_name or "",
        ))

    # Issue local JWT (include role so admin via Google OAuth gets admin access)
    jwt_token = auth_handler.create_token(user.id, user.email, role=user.role, username=user.username or "")

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
    avatar_url: Optional[str] = None


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
    if data.avatar_url is not None:
        user.avatar_url = data.avatar_url
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
    _r2 = await _get_redis()
    _uid2 = str(user.id)
    if user.role == "admin":
        _plan2 = "ultimate"
    else:
        _plan2 = (await _r2.get(f"user:{_uid2}:plan")) or "free"
        if _plan2 == "trial":
            _trial_exp2 = int((await _r2.get(f"user:{_uid2}:trial_expires_at")) or 0)
            if _trial_exp2 and time.time() > _trial_exp2:
                await _r2.set(f"user:{_uid2}:plan", "free")
                _plan2 = "free"
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "avatar_url": user.avatar_url,
        "role": user.role,
        "plan": _plan2,
        "is_admin": user.role == "admin",
    }


AVATAR_DIR = "/app/static/avatars"

@router.post("/upload-avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    token: str = Depends(get_token),
    db: AsyncSession = Depends(get_db),
):
    """Upload profile avatar. Accepts JPG, PNG, WEBP. Max 5MB."""
    payload = auth_handler.verify_token(token)
    user_id = payload["sub"]

    # Validate content type
    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Format harus JPG, PNG, atau WEBP")

    # Validate file size (5MB max)
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Ukuran foto maksimal 5MB")

    # Determine extension
    ext_map = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}
    ext = ext_map[file.content_type]

    # Ensure directory exists
    os.makedirs(AVATAR_DIR, exist_ok=True)

    # Save file
    filename = f"{user_id}.{ext}"
    filepath = os.path.join(AVATAR_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(contents)

    avatar_url = f"/auth/static/avatars/{filename}"

    # Update user record in DB
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user:
        user.avatar_url = avatar_url
        await db.commit()
        await db.refresh(user)

    logger.info("avatar_uploaded", user_id=user_id, avatar_url=avatar_url)
    return {"avatar_url": avatar_url, "status": "ok"}
