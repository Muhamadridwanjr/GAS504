from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_db
from src.db.repositories.plan_repo import PlanRepo
from src.core.plan_manager import PlanManager
from src.api.models import PlanCreateRequest, PlanUpdateRequest, PlanResponse

router = APIRouter(tags=["Plans"])

def get_user_id(x_user_id: str = Header(...)) -> str:
    return x_user_id

@router.post("/plans", status_code=201)
async def create_plan(req: PlanCreateRequest, user_id: str = Depends(get_user_id), db: AsyncSession = Depends(get_db)):
    mgr = PlanManager(PlanRepo(db))
    plan = await mgr.create_plan(user_id, req.model_dump())
    return {"id": plan.id, "user_id": plan.user_id, "title": plan.title, "created_at": str(plan.created_at)}

@router.get("/plans")
async def list_plans(status: str | None = None, symbol: str | None = None, from_date: str | None = None,
                     to_date: str | None = None, limit: int = 50, offset: int = 0,
                     user_id: str = Depends(get_user_id), db: AsyncSession = Depends(get_db)):
    mgr = PlanManager(PlanRepo(db))
    plans = await mgr.list_plans(user_id, status=status, symbol=symbol, limit=limit, offset=offset)
    data = [{"id": p.id, "title": p.title, "plan_date": str(p.plan_date), "symbol": p.symbol,
             "direction": p.direction, "entry_price": p.entry_price, "stop_loss": p.stop_loss,
             "take_profit": p.take_profit, "status": p.status, "created_at": str(p.created_at)} for p in plans]
    return {"total": len(data), "data": data}

@router.get("/plans/{plan_id}")
async def get_plan(plan_id: int, user_id: str = Depends(get_user_id), db: AsyncSession = Depends(get_db)):
    mgr = PlanManager(PlanRepo(db))
    plan = await mgr.get_plan(user_id, plan_id)
    if not plan: raise HTTPException(404, "Plan not found")
    return {"id": plan.id, "title": plan.title, "description": plan.description, "plan_date": str(plan.plan_date),
            "symbol": plan.symbol, "direction": plan.direction, "entry_price": plan.entry_price,
            "stop_loss": plan.stop_loss, "take_profit": plan.take_profit, "notes": plan.notes,
            "status": plan.status, "created_at": str(plan.created_at)}

@router.put("/plans/{plan_id}")
async def update_plan(plan_id: int, req: PlanUpdateRequest, user_id: str = Depends(get_user_id), db: AsyncSession = Depends(get_db)):
    mgr = PlanManager(PlanRepo(db))
    plan = await mgr.update_plan(user_id, plan_id, req.model_dump(exclude_unset=True))
    if not plan: raise HTTPException(404, "Plan not found")
    return {"id": plan.id, "status": "updated"}

@router.delete("/plans/{plan_id}", status_code=204)
async def delete_plan(plan_id: int, user_id: str = Depends(get_user_id), db: AsyncSession = Depends(get_db)):
    mgr = PlanManager(PlanRepo(db))
    ok = await mgr.delete_plan(user_id, plan_id)
    if not ok: raise HTTPException(404, "Plan not found")

@router.patch("/plans/{plan_id}/complete")
async def complete_plan(plan_id: int, user_id: str = Depends(get_user_id), db: AsyncSession = Depends(get_db)):
    mgr = PlanManager(PlanRepo(db))
    plan = await mgr.complete_plan(user_id, plan_id)
    if not plan: raise HTTPException(404, "Plan not found")
    return {"id": plan.id, "status": plan.status}

@router.patch("/plans/{plan_id}/cancel")
async def cancel_plan(plan_id: int, user_id: str = Depends(get_user_id), db: AsyncSession = Depends(get_db)):
    mgr = PlanManager(PlanRepo(db))
    plan = await mgr.cancel_plan(user_id, plan_id)
    if not plan: raise HTTPException(404, "Plan not found")
    return {"id": plan.id, "status": plan.status}
