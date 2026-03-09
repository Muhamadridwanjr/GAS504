from fastapi import Header, HTTPException

async def get_user_id(x_user_id: str = Header(None, alias="X-User-ID")):
    """
    Dependency untuk mengekstrak ID pengguna dari Header.
    Fungsi ini digunakan bersama gas-gateway-api yang mengeforward user info.
    """
    if not x_user_id:
        raise HTTPException(status_code=401, detail="X-User-ID header missing or invalid.")
    return x_user_id
