from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_db
from src.db.repositories.template_repo import TemplateRepo
from src.db.repositories.favorite_repo import FavoriteRepo
from src.core.template_manager import TemplateManager
from src.core.favorites_manager import FavoritesManager
from src.api.models import ChartDataRequest, TemplateCreateRequest

router = APIRouter(tags=["Chart"])

def get_user_id(x_user_id: str = Header(...)) -> str: return x_user_id

@router.post("/chart/data")
async def get_chart_data(req: ChartDataRequest, request: Request):
    orch = request.app.state.orchestrator
    return await orch.get_chart_data(req.symbol, req.timeframe, req.from_ts, req.to_ts, req.count, req.indicators, req.include_smc)

@router.get("/chart/templates")
async def list_templates(user_id: str = Depends(get_user_id), db: AsyncSession = Depends(get_db)):
    mgr = TemplateManager(TemplateRepo(db))
    tmpls = await mgr.list_templates(user_id)
    return {"templates": [{"id": t.id, "name": t.name, "created_at": str(t.created_at)} for t in tmpls]}

@router.post("/chart/templates", status_code=201)
async def create_template(req: TemplateCreateRequest, user_id: str = Depends(get_user_id), db: AsyncSession = Depends(get_db)):
    mgr = TemplateManager(TemplateRepo(db))
    t = await mgr.create_template(user_id, req.name, req.layout)
    return {"id": t.id, "name": t.name}

@router.get("/chart/templates/{tmpl_id}")
async def get_template(tmpl_id: int, user_id: str = Depends(get_user_id), db: AsyncSession = Depends(get_db)):
    mgr = TemplateManager(TemplateRepo(db))
    t = await mgr.get_template(user_id, tmpl_id)
    if not t: raise HTTPException(404, "Template not found")
    return {"id": t.id, "name": t.name, "layout": t.layout, "created_at": str(t.created_at)}

@router.put("/chart/templates/{tmpl_id}")
async def update_template(tmpl_id: int, req: TemplateCreateRequest, user_id: str = Depends(get_user_id), db: AsyncSession = Depends(get_db)):
    mgr = TemplateManager(TemplateRepo(db))
    t = await mgr.update_template(user_id, tmpl_id, name=req.name, layout=req.layout)
    if not t: raise HTTPException(404, "Template not found")
    return {"id": t.id, "status": "updated"}

@router.delete("/chart/templates/{tmpl_id}", status_code=204)
async def delete_template(tmpl_id: int, user_id: str = Depends(get_user_id), db: AsyncSession = Depends(get_db)):
    mgr = TemplateManager(TemplateRepo(db))
    if not await mgr.delete_template(user_id, tmpl_id): raise HTTPException(404, "Template not found")

@router.get("/chart/favorites")
async def list_favorites(user_id: str = Depends(get_user_id), db: AsyncSession = Depends(get_db)):
    mgr = FavoritesManager(FavoriteRepo(db))
    favs = await mgr.list_favorites(user_id)
    return {"favorites": [{"id": f.id, "indicator": f.indicator} for f in favs]}

@router.post("/chart/favorites", status_code=201)
async def add_favorite(indicator: str, user_id: str = Depends(get_user_id), db: AsyncSession = Depends(get_db)):
    mgr = FavoritesManager(FavoriteRepo(db))
    f = await mgr.add_favorite(user_id, indicator)
    return {"id": f.id, "indicator": f.indicator}

@router.delete("/chart/favorites/{indicator}", status_code=204)
async def remove_favorite(indicator: str, user_id: str = Depends(get_user_id), db: AsyncSession = Depends(get_db)):
    mgr = FavoritesManager(FavoriteRepo(db))
    if not await mgr.remove_favorite(user_id, indicator): raise HTTPException(404, "Favorite not found")
