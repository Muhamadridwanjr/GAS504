"""Business logic for trading plan management."""
from __future__ import annotations
from src.db.repositories.plan_repo import PlanRepo
from src.lib.logger import get_logger
logger = get_logger(__name__)

class PlanManager:
    def __init__(self, repo: PlanRepo):
        self.repo = repo

    async def create_plan(self, user_id: str, data: dict):
        plan = await self.repo.create(user_id, **data)
        logger.info("Created plan %d for user %s", plan.id, user_id)
        return plan

    async def get_plan(self, user_id: str, plan_id: int):
        return await self.repo.get_by_id(user_id, plan_id)

    async def list_plans(self, user_id: str, **filters):
        return await self.repo.list_plans(user_id, **filters)

    async def update_plan(self, user_id: str, plan_id: int, data: dict):
        plan = await self.repo.get_by_id(user_id, plan_id)
        if not plan: return None
        return await self.repo.update(plan, **data)

    async def delete_plan(self, user_id: str, plan_id: int) -> bool:
        plan = await self.repo.get_by_id(user_id, plan_id)
        if not plan: return False
        await self.repo.delete(plan)
        return True

    async def complete_plan(self, user_id: str, plan_id: int):
        plan = await self.repo.get_by_id(user_id, plan_id)
        if not plan: return None
        return await self.repo.set_status(plan, "completed")

    async def cancel_plan(self, user_id: str, plan_id: int):
        plan = await self.repo.get_by_id(user_id, plan_id)
        if not plan: return None
        return await self.repo.set_status(plan, "canceled")
