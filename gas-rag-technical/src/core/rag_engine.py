"""
RAG Engine Core – orchestrates the full pipeline:
retrieve → build context → route to provider → parse response → cache.
"""
from __future__ import annotations
import json
import time
from typing import Any

from src.config import settings
from src.core.context_builder import build_prompt
from src.core.response_parser import parse_response
from src.core.exceptions import ProviderError, VectorStoreError
from src.retrieval.vector_store import VectorStore
from src.retrieval.retrievers import TechnicalRetriever
from src.providers.router import ProviderRouter
from src.market.client import MarketDataClient
from src.lib.utils import make_analysis_id, hash_query
from src.lib.logger import get_logger

logger = get_logger(__name__)


class RAGEngine:
    """
    Central orchestrator for the RAG-based technical analysis pipeline.
    """

    def __init__(
        self,
        vector_store: VectorStore,
        market_client: MarketDataClient,
        provider_router: ProviderRouter,
    ) -> None:
        self._store = vector_store
        self._market = market_client
        self._router = provider_router
        self._retriever = TechnicalRetriever(vector_store)
        self._redis: Any = None

    # ─── Cache ────────────────────────────────────────────────────────────

    async def _get_cache(self, key: str) -> dict | None:
        if self._redis is None:
            return None
        try:
            raw = await self._redis.get(f"rag:analysis:{key}")
            return json.loads(raw) if raw else None
        except Exception:  # noqa: BLE001
            return None

    async def _set_cache(self, key: str, data: dict) -> None:
        if self._redis is None:
            return
        try:
            await self._redis.setex(
                f"rag:analysis:{key}", settings.CACHE_TTL, json.dumps(data)
            )
        except Exception:  # noqa: BLE001
            pass

    async def init_cache(self) -> None:
        """Optional – connect to Redis if available."""
        try:
            import redis.asyncio as aioredis
            self._redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
            await self._redis.ping()
            logger.info("Redis cache connected")
        except Exception as exc:  # noqa: BLE001
            logger.warning("Redis not available, cache disabled: %s", exc)

    # ─── Main Pipeline ────────────────────────────────────────────────────

    async def analyze(
        self,
        symbol: str,
        timeframe: str,
        query: str,
        context: dict[str, Any] | None = None,
        model_preference: str | None = None,
        include_sources: bool = True,
        temperature: float = 0.3,
        max_tokens: int = 1500,
    ) -> dict[str, Any]:
        """
        Full RAG analysis pipeline.

        Returns a structured analysis dict.
        """
        start_ms = time.time()
        ctx = context or {}

        # 1. Cache check
        cache_key = hash_query(query, symbol, timeframe)
        if cached := await self._get_cache(cache_key):
            logger.info("Cache HIT for %s/%s", symbol, timeframe)
            return cached

        # 2. Fetch market data (non-blocking on failure)
        market_data = await self._market.get_market_context(symbol, timeframe)

        # 3. Retrieve relevant documents
        docs = await self._retriever.retrieve(
            query=query,
            symbol=symbol,
            timeframe=timeframe,
            limit=5,
            provider_preference=model_preference,
        )

        # 4. Build prompt
        system_prompt, user_prompt = build_prompt(
            query=query,
            symbol=symbol,
            timeframe=timeframe,
            market_data=market_data,
            indicators=ctx.get("indicators"),
            smc_context=ctx.get("smc"),
            retrieved_docs=docs if include_sources else [],
        )

        # 5. Route to provider and generate
        provider = self._router.get_provider(model_preference)  # type: ignore[arg-type]
        logger.info("Generating analysis via %s/%s", provider.provider_name, provider.model_name)
        try:
            raw_response = await provider.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                params={"temperature": temperature, "max_tokens": max_tokens},
            )
        except ProviderError as exc:
            logger.error("Provider error: %s", exc)
            raise

        # 6. Parse structured response
        parsed = parse_response(raw_response)

        # 7. Build final result
        elapsed_ms = int((time.time() - start_ms) * 1000)
        analysis_id = make_analysis_id(symbol, timeframe)

        result: dict[str, Any] = {
            "id": analysis_id,
            "symbol": symbol,
            "timeframe": timeframe,
            "timestamp": int(time.time()),
            "summary": parsed.get("summary", ""),
            "key_levels": parsed.get("key_levels", {"support": [], "resistance": []}),
            "signal": parsed.get("signal", "NEUTRAL"),
            "confidence": parsed.get("confidence", 0.5),
            "entry": parsed.get("entry", {"price": None, "stop_loss": None, "take_profit": []}),
            "reasoning": parsed.get("reasoning", ""),
            "short_term_bias": parsed.get("short_term_bias", "sideways"),
            "key_risks": parsed.get("key_risks", []),
            "provider_used": provider.provider_name,
            "model_used": provider.model_name,
            "processing_time_ms": elapsed_ms,
        }

        if include_sources and docs:
            result["sources"] = [
                {
                    "title": d.get("title", "Document"),
                    "source": d.get("source", ""),
                    "relevance": d.get("relevance", 0.0),
                }
                for d in docs
            ]

        # 8. Cache result
        await self._set_cache(cache_key, result)

        # 9. (Async) Store analysis in knowledge base for future retrieval
        await self._store_analysis(result, symbol, timeframe)

        return result

    async def _store_analysis(
        self, result: dict[str, Any], symbol: str, timeframe: str
    ) -> None:
        """Persist the analysis back into the vector store for future lookups."""
        try:
            from src.retrieval.embeddings import get_embedding
            text = f"{result['summary']} {result['reasoning']}"
            embedding = await get_embedding(text)
            await self._store.add_documents(
                texts=[text],
                embeddings=[embedding],
                metadatas=[{
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "signal": result.get("signal", ""),
                    "source": f"auto-analysis:{result['id']}",
                    "title": f"Analysis {symbol}/{timeframe} {result['id']}",
                }],
                ids=[result["id"]],
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not store analysis in vector store: %s", exc)
