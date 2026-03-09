from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from src.config import settings
from src.db.database import get_db
from src.db.repositories.signal_repo import SignalRepository
from src.core.service import SignalCoreService
from src.lib.logger import logger

security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        if settings.DEBUG:
            logger.warning("No credentials found, but DEBUG is True. Bypassing auth with dummy user.")
            return {"user_id": "debug-user", "token": "debug-token", "role": "admin"}
        # Check if internal API Key instead
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = credentials.credentials
    try:
        # Validate JWT using the shared secret
        # In a real app we'd fetch JWKS or use the shared symetric key
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        return {"user_id": payload.get("sub"), "token": token, "role": payload.get("role", "user")}
    except jwt.ExpiredSignatureError:
        if settings.DEBUG:
            logger.warning("Token expired, but DEBUG is True. Bypassing auth.")
            return {"user_id": "debug-user-expired", "token": token, "role": "user"}
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        if settings.DEBUG:
            logger.warning(f"Invalid token ({e}), but DEBUG is True. Bypassing auth.")
            return {"user_id": "debug-user-invalid", "token": token, "role": "user"}
        logger.error(f"Invalid token: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def get_signal_service(session: AsyncSession = Depends(get_db)) -> SignalCoreService:
    repo = SignalRepository(session)
    return SignalCoreService(repo)
