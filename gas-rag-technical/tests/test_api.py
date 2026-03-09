"""Integration tests for the FastAPI endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_health_endpoint():
    """GET /health should return 200 with status=ok."""
    # Patch all startup dependencies
    with (
        patch("src.retrieval.vector_store.VectorStore.initialize", new_callable=AsyncMock),
        patch("src.core.rag_engine.RAGEngine.init_cache", new_callable=AsyncMock),
        patch("src.knowledge.indexer.run_background_indexer", new_callable=AsyncMock),
        patch("src.config.settings.ENVIRONMENT", "testing"),
    ):
        from src.main import app
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "gas-rag-technical"


@pytest.mark.asyncio
async def test_analyze_endpoint_returns_analysis(mock_vector_store, mock_market_client, mock_provider_router):
    """POST /analyze should return a structured analysis response."""
    from src.main import app

    # Manually set app state (bypass lifespan)
    from src.core.rag_engine import RAGEngine

    engine = RAGEngine(
        vector_store=mock_vector_store,
        market_client=mock_market_client,
        provider_router=mock_provider_router,
    )
    engine._redis = None

    app.state.rag_engine = engine

    with patch("src.retrieval.retrievers.get_embedding", new_callable=AsyncMock) as mock_emb:
        mock_emb.return_value = [0.0] * 128

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/analyze",
                json={
                    "symbol": "XAUUSD",
                    "timeframe": "H4",
                    "query": "Analisis level kunci hari ini",
                    "model_preference": "openai",
                    "include_sources": False,
                },
            )

    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "XAUUSD"
    assert data["signal"] in ("BUY", "SELL", "NEUTRAL")
    assert "summary" in data
    assert "key_levels" in data
    assert "provider_used" in data
