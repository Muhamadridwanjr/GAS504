"""Unit tests for PlanManager — installs sqlalchemy in test env."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import date


def make_plan(id=1, status="active"):
    p = MagicMock()
    p.id = id
    p.user_id = "user_123"
    p.title = "XAUUSD BUY"
    p.plan_date = date(2026, 3, 4)
    p.symbol = "XAUUSD"
    p.direction = "BUY"
    p.entry_price = 2900.0
    p.stop_loss = 2880.0
    p.take_profit = 2940.0
    p.status = status
    p.created_at = "2026-03-04T00:00:00"
    return p


@pytest.mark.asyncio
async def test_create_plan():
    from src.core.plan_manager import PlanManager
    repo = AsyncMock()
    plan = make_plan()
    repo.create.return_value = plan
    mgr = PlanManager(repo)
    result = await mgr.create_plan("user_123", {"title": "XAUUSD BUY", "symbol": "XAUUSD"})
    assert result.id == 1
    repo.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_plan_found():
    from src.core.plan_manager import PlanManager
    repo = AsyncMock()
    repo.get_by_id.return_value = make_plan()
    mgr = PlanManager(repo)
    result = await mgr.get_plan("user_123", 1)
    assert result.id == 1


@pytest.mark.asyncio
async def test_get_plan_not_found():
    from src.core.plan_manager import PlanManager
    repo = AsyncMock()
    repo.get_by_id.return_value = None
    mgr = PlanManager(repo)
    result = await mgr.get_plan("user_123", 999)
    assert result is None


@pytest.mark.asyncio
async def test_delete_plan_success():
    from src.core.plan_manager import PlanManager
    repo = AsyncMock()
    plan = make_plan()
    repo.get_by_id.return_value = plan
    mgr = PlanManager(repo)
    result = await mgr.delete_plan("user_123", 1)
    assert result is True
    repo.delete.assert_awaited_once_with(plan)


@pytest.mark.asyncio
async def test_delete_plan_not_found():
    from src.core.plan_manager import PlanManager
    repo = AsyncMock()
    repo.get_by_id.return_value = None
    mgr = PlanManager(repo)
    result = await mgr.delete_plan("user_123", 999)
    assert result is False


@pytest.mark.asyncio
async def test_complete_plan():
    from src.core.plan_manager import PlanManager
    repo = AsyncMock()
    completed = make_plan(status="completed")
    repo.get_by_id.return_value = make_plan()
    repo.set_status.return_value = completed
    mgr = PlanManager(repo)
    result = await mgr.complete_plan("user_123", 1)
    assert result.status == "completed"


@pytest.mark.asyncio
async def test_cancel_plan():
    from src.core.plan_manager import PlanManager
    repo = AsyncMock()
    canceled = make_plan(status="canceled")
    repo.get_by_id.return_value = make_plan()
    repo.set_status.return_value = canceled
    mgr = PlanManager(repo)
    result = await mgr.cancel_plan("user_123", 1)
    assert result.status == "canceled"


@pytest.mark.asyncio
async def test_update_plan_not_found():
    from src.core.plan_manager import PlanManager
    repo = AsyncMock()
    repo.get_by_id.return_value = None
    mgr = PlanManager(repo)
    result = await mgr.update_plan("user_123", 999, {"title": "New"})
    assert result is None
