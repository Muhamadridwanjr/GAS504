"""
/terminal/alerts – CRUD proxy for gas-alert-engine.
"""
from fastapi import APIRouter, Query
from src.config import settings
from src.services.client import fetch_json

router = APIRouter()


@router.get("/terminal/alerts")
async def list_alerts(user_id: str = Query(...)):
    data = await fetch_json(
        f"{settings.ALERT_ENGINE_URL}/alerts",
        params={"user_id": user_id},
        timeout=8.0,
    )
    if "error" in data:
        return {"alerts": [], "status": "unavailable"}
    return data


@router.post("/terminal/alerts")
async def create_alert(body: dict):
    data = await fetch_json(
        f"{settings.ALERT_ENGINE_URL}/alerts",
        method="POST",
        json_body=body,
        timeout=8.0,
    )
    return data


@router.put("/terminal/alerts/{alert_id}")
async def update_alert(alert_id: str, body: dict):
    data = await fetch_json(
        f"{settings.ALERT_ENGINE_URL}/alerts/{alert_id}",
        method="PUT",
        json_body=body,
        timeout=8.0,
    )
    return data


@router.delete("/terminal/alerts/{alert_id}")
async def delete_alert(alert_id: str):
    data = await fetch_json(
        f"{settings.ALERT_ENGINE_URL}/alerts/{alert_id}",
        method="DELETE",
        timeout=8.0,
    )
    return data


@router.post("/terminal/alerts/{alert_id}/activate")
async def activate_alert(alert_id: str):
    data = await fetch_json(
        f"{settings.ALERT_ENGINE_URL}/alerts/{alert_id}/activate",
        method="POST",
        timeout=8.0,
    )
    return data


@router.post("/terminal/alerts/{alert_id}/deactivate")
async def deactivate_alert(alert_id: str):
    data = await fetch_json(
        f"{settings.ALERT_ENGINE_URL}/alerts/{alert_id}/deactivate",
        method="POST",
        timeout=8.0,
    )
    return data
