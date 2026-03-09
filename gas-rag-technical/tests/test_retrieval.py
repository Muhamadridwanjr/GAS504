"""Tests for the RAG retrieval pipeline."""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_retrieval_returns_empty_on_no_store():
    """Retriever should return empty list when vector store returns nothing."""
    from src.retrieval.retrievers import TechnicalRetriever

    mock_store = AsyncMock()
    mock_store.query.return_value = []

    with patch("src.retrieval.retrievers.get_embedding", new_callable=AsyncMock) as mock_emb:
        mock_emb.return_value = [0.1] * 128
        retriever = TechnicalRetriever(store=mock_store)
        results = await retriever.retrieve(
            query="support and resistance levels for gold",
            symbol="XAUUSD",
            limit=5,
        )

    assert isinstance(results, list)
    assert len(results) == 0


@pytest.mark.asyncio
async def test_retrieval_passes_symbol_filter():
    """Symbol filter should be included in the vector store query."""
    from src.retrieval.retrievers import TechnicalRetriever

    mock_store = AsyncMock()
    mock_store.query.return_value = [
        {"text": "XAUUSD support at 1990", "source": "doc1", "relevance": 0.9, "score": 0.9, "title": "Test", "metadata": {}}
    ]

    with patch("src.retrieval.retrievers.get_embedding", new_callable=AsyncMock) as mock_emb:
        mock_emb.return_value = [0.1] * 128
        retriever = TechnicalRetriever(store=mock_store)
        results = await retriever.retrieve(
            query="support levels for XAUUSD",
            symbol="XAUUSD",
            limit=5,
        )

    assert len(results) == 1
    assert "XAUUSD" in results[0]["text"]
    # Verify that the where filter was used
    call_kwargs = mock_store.query.call_args[1]
    assert call_kwargs.get("where") is not None


@pytest.mark.asyncio
async def test_retrieval_embedding_failure_returns_empty():
    """When embedding fails, retriever should return empty list, not raise."""
    from src.retrieval.retrievers import TechnicalRetriever

    mock_store = AsyncMock()

    with patch("src.retrieval.retrievers.get_embedding", new_callable=AsyncMock) as mock_emb:
        mock_emb.side_effect = Exception("OpenAI API error")
        retriever = TechnicalRetriever(store=mock_store)
        results = await retriever.retrieve(query="gold analysis", symbol="XAUUSD")

    assert results == []
