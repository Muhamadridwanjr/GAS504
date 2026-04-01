from fastapi import APIRouter
from fastapi.responses import FileResponse
import os

router = APIRouter(prefix="/terminal/download", tags=["download"])

APK_PATH = "/app/GAS-Terminal-v1.0.apk"

@router.get("/apk")
async def download_apk():
    if os.path.exists(APK_PATH):
        return FileResponse(
            APK_PATH,
            media_type="application/vnd.android.package-archive",
            filename="GAS-Terminal-v1.0.apk",
            headers={"Content-Disposition": "attachment; filename=GAS-Terminal-v1.0.apk"}
        )
    return {"error": "APK not found on server"}

@router.get("/info")
async def apk_info():
    size = os.path.getsize(APK_PATH) if os.path.exists(APK_PATH) else 0
    return {
        "name": "GAS Terminal",
        "version": "1.0.0",
        "size_mb": round(size / 1024 / 1024, 1),
        "platform": "Android (5.0+)",
        "min_sdk": 23,
        "available": os.path.exists(APK_PATH),
        "download_url": "/terminal/download/apk"
    }
