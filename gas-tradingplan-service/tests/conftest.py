import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import date

@pytest.fixture
def mock_repo():
    """Mock PlanRepo with sensible defaults."""
    from unittest.mock import AsyncMock
    repo = AsyncMock()
    return repo

@pytest.fixture
def sample_plan():
    plan = MagicMock()
    plan.id = 1
    plan.user_id = "user_123"
    plan.title = "Buy XAUUSD"
    plan.plan_date = date(2026, 3, 4)
    plan.symbol = "XAUUSD"
    plan.direction = "BUY"
    plan.entry_price = 2900.0
    plan.stop_loss = 2880.0
    plan.take_profit = 2940.0
    plan.status = "active"
    return plan
