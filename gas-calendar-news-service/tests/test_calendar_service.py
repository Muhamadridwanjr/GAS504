"""Unit tests for CalendarService — mocked repo."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import AsyncMock, MagicMock
from src.core.calendar_service import CalendarService


def make_event(id=1, currency="USD", impact="high", title="FOMC Meeting"):
    e = MagicMock()
    e.id = id
    e.currency = currency
    e.impact = impact
    e.title = title
    e.event_date = "2026-03-10"
    return e


@pytest.mark.asyncio
async def test_get_events_by_currency():
    repo = AsyncMock()
    repo.get_by_currency.return_value = [make_event()]
    svc = CalendarService(repo)
    result = await svc.get_events(currency="USD")
    assert len(result) == 1
    assert result[0].currency == "USD"


@pytest.mark.asyncio
async def test_get_events_no_filter():
    repo = AsyncMock()
    repo.get_all.return_value = [make_event(), make_event(id=2, currency="EUR")]
    svc = CalendarService(repo)
    result = await svc.get_events()
    assert len(result) == 2


@pytest.mark.asyncio
async def test_get_events_empty():
    repo = AsyncMock()
    repo.get_by_currency.return_value = []
    svc = CalendarService(repo)
    result = await svc.get_events(currency="JPY")
    assert result == []
