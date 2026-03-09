from fastapi import Header, HTTPException, Depends
from typing import Optional

async def get_user_id(x_user_id: Optional[str] = Header(None)) -> str:
    # In a real scenario, the gateway should ALwAYS pass X-User-ID.
    # We can make it optional for testing or strict for production.
    if not x_user_id:
        # We can mock this for local development if needed, but typically:
        # raise HTTPException(status_code=401, detail="X-User-ID header missing")
        return "system" # Fallback for now
    return x_user_id
