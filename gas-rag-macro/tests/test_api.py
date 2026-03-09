"""
API endpoint tests for gas-rag-macro.
"""
import pytest
from unittest.mock import AsyncMock, patch

from src.api.models import MacroAnalyzeResponse, KeyFactor


def _mock_response(symbol: str = "XAUUSD") -> MacroAnalyzeResponse:
    return MacroAnalyzeResponse(
        id="macro_test1234",
        symbol=symbol,
        timestamp=1700001234,
        summary="Bearish macro outlook for gold due to strong USD.",
        sentiment="bearish",
        confidence=0.75,
        key_factors=[KeyFactor(factor="CPI", impact="USD strength", probability=0.7)],
        news=[],
        calendar_events=[],
        historical_reaction="Gold dropped 0.5% on CPI beat.",
        sources=["Bloomberg"],
        provider_used="openai",
        model_used="gpt-4o",
        processing_time_ms=0,
    )


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "gas-rag-macro"
    assert "version" in data
    assert "environment" in data


def test_providers_endpoint(client):
    response = client.get("/macro/providers")
    assert response.status_code == 200
    data = response.json()
    assert "providers" in data
    assert "default" in data
    assert isinstance(data["providers"], list)


def test_analyze_endpoint_success(client):
    with patch(
        "src.core.rag_engine.RAGEngine.analyze",
        new=AsyncMock(return_value=_mock_response("XAUUSD")),
    ):
        payload = {
            "symbol": "XAUUSD",
            "query": "What is the macro outlook for gold in the next 24 hours?",
            "time_horizon": "24h",
            "include_news": False,
            "include_calendar": False,
            "include_price_data": False,
            "model_preference": "openai",
        }
        response = client.post("/macro/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "XAUUSD"
    assert "summary" in data
    assert data["sentiment"] in ("bullish", "bearish", "neutral")
    assert 0.0 <= data["confidence"] <= 1.0
    assert isinstance(data["key_factors"], list)
    assert "provider_used" in data
    assert "model_used" in data


def test_analyze_endpoint_missing_symbol(client):
    """Missing required 'symbol' field should return 422 Unprocessable Entity."""
    payload = {"query": "test query"}
    response = client.post("/macro/analyze", json=payload)
    assert response.status_code == 422


def test_knowledge_update_requires_auth(client):
    response = client.post("/knowledge/update")
    assert response.status_code == 403


def test_knowledge_update_with_valid_key(client):
    with patch(
        "src.knowledge.indexer.index_knowledge_base",
        new=AsyncMock(return_value=5),
    ):
        response = client.post(
            "/knowledge/update",
            headers={"X-API-Key": "gas-internal-secret-key"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["documents_indexed"] == 5
