"""
RAG Engine – core orchestration for gas-rag-macro.

Pipeline:
  1. Fetch news articles.
  2. Fetch economic calendar events.
  3. Fetch market price data.
  4. Retrieve similar docs from vector store.
  5. Build prompt context.
  6. Generate analysis via AI provider.
  7. Parse response and cache.
"""
from __future__ import annotations
import json

import redis.asyncio as aioredis

from src.api.models import MacroAnalyzeRequest, MacroAnalyzeResponse
from src.config import settings
from src.core.context_builder import ContextBuilder
from src.core.response_parser import ResponseParser
from src.core.exceptions import ProviderError
from src.fetchers.news import NewsFetcher
from src.fetchers.calendar import CalendarFetcher
from src.lib.logger import get_logger
from src.lib.utils import build_cache_key

logger = get_logger(__name__)


class RAGEngine:
    """
    Orchestrates the full RAG pipeline for macroeconomic analysis.

    Args:
        vector_store: Initialized VectorStore instance.
        market_client: MarketDataClient for price data.
        provider_router: ProviderRouter for AI generation.
    """

    def __init__(self, vector_store, market_client, provider_router):
        self.vector_store = vector_store
        self.market_client = market_client
        self.provider_router = provider_router
        self.news_fetcher = NewsFetcher()
        self.calendar_fetcher = CalendarFetcher()
        self.context_builder = ContextBuilder()
        self.response_parser = ResponseParser()
        self._redis: aioredis.Redis | None = None

    async def init_cache(self) -> None:
        """Initialize Redis connection for result caching."""
        try:
            self._redis = aioredis.from_url(
                settings.REDIS_URL, encoding="utf-8", decode_responses=True
            )
            await self._redis.ping()
            logger.info("rag_engine.cache.connected")
        except Exception as exc:
            logger.warning("rag_engine.cache.unavailable", error=str(exc))
            self._redis = None

    # ── Cache helpers ─────────────────────────────────────────────────────────

    async def _get_cache(self, key: str) -> MacroAnalyzeResponse | None:
        if not self._redis:
            return None
        try:
            raw = await self._redis.get(key)
            if raw:
                return MacroAnalyzeResponse(**json.loads(raw))
        except Exception:
            pass
        return None

    async def _set_cache(self, key: str, response: MacroAnalyzeResponse) -> None:
        if not self._redis:
            return
        try:
            await self._redis.setex(key, settings.CACHE_TTL, response.model_dump_json())
        except Exception:
            pass

    # ── Main pipeline ─────────────────────────────────────────────────────────

    async def analyze(self, request: MacroAnalyzeRequest) -> MacroAnalyzeResponse:
        """
        Run the full macro RAG pipeline and return analysis.

        Args:
            request: MacroAnalyzeRequest from the API.

        Returns:
            MacroAnalyzeResponse with structured macro analysis.
        """
        cache_key = build_cache_key(
            request.symbol,
            request.time_horizon,
            request.model_preference,
            str(hash(request.query)),
        )

        # 1. Check cache
        cached = await self._get_cache(cache_key)
        if cached:
            logger.info("rag_engine.cache.hit", symbol=request.symbol)
            return cached

        # 2. Fetch external data in parallel
        news_articles: list[dict] = []
        calendar_events: list[dict] = []
        price_data: dict | None = None

        if request.include_news:
            try:
                news_articles = await self.news_fetcher.fetch(request.symbol, limit=10)
            except Exception as exc:
                logger.warning("rag_engine.news.error", error=str(exc))

        if request.include_calendar:
            try:
                calendar_events = await self.calendar_fetcher.fetch(request.symbol)
            except Exception as exc:
                logger.warning("rag_engine.calendar.error", error=str(exc))

        if request.include_price_data:
            try:
                price_data = await self.market_client.get_price_data(request.symbol)
            except Exception as exc:
                logger.warning("rag_engine.market.error", error=str(exc))

        # 3. Retrieve from vector store
        retrieved_docs: list[dict] = []
        try:
            retrieved_docs = await self.vector_store.similarity_search(
                query=request.query, n_results=5, filter_symbol=request.symbol
            )
        except Exception as exc:
            logger.warning("rag_engine.retrieval.error", error=str(exc))

        # 4. Build context & generate
        system_prompt, user_prompt = self.context_builder.build(
            query=request.query,
            symbol=request.symbol,
            time_horizon=request.time_horizon,
            news_articles=news_articles,
            calendar_events=calendar_events,
            price_data=price_data,
            retrieved_docs=retrieved_docs,
        )

        try:
            raw_text, provider_name, model_name = await self.provider_router.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                provider_preference=request.model_preference,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
        except Exception as exc:
            raise ProviderError(f"AI generation failed: {exc}") from exc

        # 5. Parse response
        result = self.response_parser.parse(
            raw_text=raw_text,
            symbol=request.symbol,
            news_articles=news_articles,
            calendar_events=calendar_events,
            provider_used=provider_name,
            model_used=model_name,
        )

        # 6. Cache and return
        await self._set_cache(cache_key, result)
        logger.info("rag_engine.analyze.done", symbol=request.symbol, provider=provider_name)
        return result
