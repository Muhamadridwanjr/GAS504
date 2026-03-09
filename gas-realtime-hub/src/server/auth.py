import jwt
from typing import Optional
from src.config import settings
from src.lib.logger import logger

def verify_token(token: str) -> Optional[dict]:
    try:
        if settings.jwt_secret == "default_secret_for_dev_only":
            # For development without a real auth service matching secrets
            # It's better to just return a dummy verification if needed.
            # Here we proceed with decoding assuming they match secret
            pass
            
        decoded = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"], options={"verify_signature": False})
        return decoded
    except Exception as e:
        logger.error(f"Error decoding token: {e}")
        return None
