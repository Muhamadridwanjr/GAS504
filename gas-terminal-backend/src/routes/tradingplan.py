"""
/terminal/plans – CRUD proxy for gas-tradingplan-service.
"""
from fastapi import APIRouter, Query
from src.config import settings
from src.services.client import fetch_json

router = APIRouter()


@router.get("/terminal/plans")
async def list_plans(user_id: str = Query(...)):
    data = await fetch_json(
        f"{settings.TRADINGPLAN_URL}/plans",
        params={"user_id": user_id},
        timeout=8.0,
    )
    if "error" in data:
        return {"plans": [], "status": "unavailable"}
    return data


@router.post("/terminal/plans")
async def create_plan(body: dict):
    data = await fetch_json(
        f"{settings.TRADINGPLAN_URL}/plans",
        method="POST",
        json_body=body,
        timeout=8.0,
    )
    return data


@router.get("/terminal/plans/{plan_id}")
async def get_plan(plan_id: str):
    data = await fetch_json(f"{settings.TRADINGPLAN_URL}/plans/{plan_id}", timeout=8.0)
    return data


@router.put("/terminal/plans/{plan_id}")
async def update_plan(plan_id: str, body: dict):
    data = await fetch_json(
        f"{settings.TRADINGPLAN_URL}/plans/{plan_id}",
        method="PUT",
        json_body=body,
        timeout=8.0,
    )
    return data


@router.delete("/terminal/plans/{plan_id}")
async def delete_plan(plan_id: str):
    data = await fetch_json(
        f"{settings.TRADINGPLAN_URL}/plans/{plan_id}",
        method="DELETE",
        timeout=8.0,
    )
    return data


@router.patch("/terminal/plans/{plan_id}/complete")
async def complete_plan(plan_id: str):
    data = await fetch_json(
        f"{settings.TRADINGPLAN_URL}/plans/{plan_id}/complete",
        method="PATCH",
        timeout=8.0,
    )
    return data


@router.patch("/terminal/plans/{plan_id}/cancel")
async def cancel_plan(plan_id: str):
    data = await fetch_json(
        f"{settings.TRADINGPLAN_URL}/plans/{plan_id}/cancel",
        method="PATCH",
        timeout=8.0,
    )
    return data
