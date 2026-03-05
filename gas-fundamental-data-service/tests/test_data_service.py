"""Unit tests for fundamental DataService — mocked repo."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import AsyncMock, MagicMock
from src.core.data_service import DataService


def make_record(id=1, indicator="interest_rate", value=5.25, country="US"):
    r = MagicMock()
    r.id = id
    r.indicator = indicator
    r.value = value
    r.country = country
    r.date = "2026-01-01"
    return r


@pytest.mark.asyncio
async def test_get_by_indicator_returns_list():
    repo = AsyncMock()
    repo.get_by_indicator.return_value = [make_record()]
    svc = DataService(repo)
    result = await svc.get_by_indicator("interest_rate", "US")
    assert len(result) == 1


@pytest.mark.asyncio
async def test_get_by_indicator_empty():
    repo = AsyncMock()
    repo.get_by_indicator.return_value = []
    svc = DataService(repo)
    result = await svc.get_by_indicator("gdp", "EU")
    assert result == []


@pytest.mark.asyncio
async def test_create_record():
    repo = AsyncMock()
    repo.create.return_value = make_record()
    svc = DataService(repo)
    result = await svc.create("interest_rate", 5.25, "US", "2026-01-01")
    assert result.value == 5.25
    repo.create.assert_awaited_once()
