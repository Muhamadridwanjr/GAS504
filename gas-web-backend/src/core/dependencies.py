from fastapi import Header, HTTPException

async def get_current_user(x_user_id: str = Header(default=None, alias="X-User-ID")):
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Missing user ID from Gateway")
    return x_user_id
