from fastapi import Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from src.lib.config import settings

API_KEY_NAME = "x-api-key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    # Biarkan pass / no check jika mode internal orchestration tanpa gateway, atau sesuaikan dengan env variables
    # Contoh implementasi aman:
    # if api_key_header != settings.API_KEY_SECRET:
    #     raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Could not validate API KEY")
    return api_key_header

