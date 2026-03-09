from fastapi import APIRouter, Depends
from ...core.dependencies import get_current_user

router = APIRouter(tags=["Certificate Generator"], dependencies=[Depends(get_current_user)])

@router.get("/certificate")
async def generate_certificate(user_id: str = Depends(get_current_user)):
    return {"url": "https://s3.amazonaws.com/cert/fake-cert.pdf", "message": "Certificate generated based on tier"}
