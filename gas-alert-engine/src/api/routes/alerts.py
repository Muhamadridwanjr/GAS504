from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional
from uuid import UUID
from src.api.models import (
    AlertCreate, AlertUpdate, AlertResponse,
    AlertListResponse, AlertHistoryListResponse,
)
from src.api.dependencies import get_alert_repo, get_current_user
from src.db.repositories.alert_repo import AlertRepository
from src.redis.cache import alert_cache
from src.lib.logger import logger

router = APIRouter(prefix="/alerts", tags=["Alerts"])


# ── POST /alerts ─────────────────────────────────────────────
@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    body: AlertCreate,
    repo: AlertRepository = Depends(get_alert_repo),
    user: dict = Depends(get_current_user),
):
    """Buat alert baru."""
    try:
        data = body.model_dump()
        data["user_id"] = user["user_id"]
        alert = await repo.create(data)

        # Rebuild cache
        await alert_cache.rebuild_cache_for_alert(alert)

        logger.info(f"Alert {alert.id} created by user {user['user_id']}")
        return alert
    except Exception as e:
        logger.error(f"Error creating alert: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# ── GET /alerts ──────────────────────────────────────────────
@router.get("", response_model=AlertListResponse)
async def list_alerts(
    active: Optional[bool] = Query(None),
    symbol: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    repo: AlertRepository = Depends(get_alert_repo),
    user: dict = Depends(get_current_user),
):
    """Daftar alert milik user."""
    alerts, total = await repo.list_by_user(
        user_id=user["user_id"],
        active=active,
        symbol=symbol,
        limit=limit,
        offset=offset,
    )
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": alerts,
    }


# ── GET /alerts/{id} ────────────────────────────────────────
@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: UUID,
    repo: AlertRepository = Depends(get_alert_repo),
    user: dict = Depends(get_current_user),
):
    """Detail alert."""
    alert = await repo.get_by_id(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    if str(alert.user_id) != str(user["user_id"]) and user.get("role") not in ("admin", "service"):
        raise HTTPException(status_code=403, detail="Forbidden")
    return alert


# ── PUT /alerts/{id} ────────────────────────────────────────
@router.put("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: UUID,
    body: AlertUpdate,
    repo: AlertRepository = Depends(get_alert_repo),
    user: dict = Depends(get_current_user),
):
    """Update alert."""
    existing = await repo.get_by_id(alert_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Alert not found")
    if str(existing.user_id) != str(user["user_id"]) and user.get("role") not in ("admin", "service"):
        raise HTTPException(status_code=403, detail="Forbidden")

    update_data = body.model_dump(exclude_unset=True)
    alert = await repo.update_alert(alert_id, update_data)

    # Rebuild cache
    if alert:
        await alert_cache.rebuild_cache_for_alert(alert)

    return alert


# ── DELETE /alerts/{id} ─────────────────────────────────────
@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: UUID,
    repo: AlertRepository = Depends(get_alert_repo),
    user: dict = Depends(get_current_user),
):
    """Hapus alert (soft delete)."""
    existing = await repo.get_by_id(alert_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Alert not found")
    if str(existing.user_id) != str(user["user_id"]) and user.get("role") not in ("admin", "service"):
        raise HTTPException(status_code=403, detail="Forbidden")

    # Remove from cache
    tf = existing.timeframe or "ALL"
    await alert_cache.remove_alert_from_set(existing.symbol, tf, str(alert_id))
    await alert_cache.invalidate_alert(str(alert_id))

    await repo.soft_delete(alert_id)


# ── POST /alerts/{id}/activate ──────────────────────────────
@router.post("/{alert_id}/activate", response_model=AlertResponse)
async def activate_alert(
    alert_id: UUID,
    repo: AlertRepository = Depends(get_alert_repo),
    user: dict = Depends(get_current_user),
):
    """Aktifkan alert."""
    existing = await repo.get_by_id(alert_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Alert not found")
    if str(existing.user_id) != str(user["user_id"]):
        raise HTTPException(status_code=403, detail="Forbidden")

    alert = await repo.set_active(alert_id, True)
    if alert:
        await alert_cache.rebuild_cache_for_alert(alert)
    return alert


# ── POST /alerts/{id}/deactivate ────────────────────────────
@router.post("/{alert_id}/deactivate", response_model=AlertResponse)
async def deactivate_alert(
    alert_id: UUID,
    repo: AlertRepository = Depends(get_alert_repo),
    user: dict = Depends(get_current_user),
):
    """Nonaktifkan alert."""
    existing = await repo.get_by_id(alert_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Alert not found")
    if str(existing.user_id) != str(user["user_id"]):
        raise HTTPException(status_code=403, detail="Forbidden")

    alert = await repo.set_active(alert_id, False)
    if alert:
        tf = alert.timeframe or "ALL"
        await alert_cache.remove_alert_from_set(alert.symbol, tf, str(alert_id))
        await alert_cache.invalidate_alert(str(alert_id))
    return alert


# ── GET /alerts/{id}/history ────────────────────────────────
@router.get("/{alert_id}/history", response_model=AlertHistoryListResponse)
async def get_alert_history(
    alert_id: UUID,
    limit: int = Query(20, le=100),
    repo: AlertRepository = Depends(get_alert_repo),
    user: dict = Depends(get_current_user),
):
    """Riwayat trigger alert."""
    existing = await repo.get_by_id(alert_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Alert not found")
    if str(existing.user_id) != str(user["user_id"]) and user.get("role") not in ("admin", "service"):
        raise HTTPException(status_code=403, detail="Forbidden")

    history = await repo.get_history(alert_id, limit=limit)
    return {"total": len(history), "data": history}
