"""
Response parser for gas-rag-macro.
Parses AI model output (JSON text) into structured Pydantic-friendly dicts.
"""
from __future__ import annotations
import json
import re
import uuid

from src.api.models import MacroAnalyzeResponse, KeyFactor, NewsArticle, CalendarEvent
from src.lib.utils import now_ts, safe_json_parse
from src.lib.logger import get_logger

logger = get_logger(__name__)


class ResponseParser:
    """Parses the raw AI text output into MacroAnalyzeResponse fields."""

    def parse(
        self,
        raw_text: str,
        symbol: str,
        news_articles: list[dict],
        calendar_events: list[dict],
        provider_used: str,
        model_used: str,
    ) -> MacroAnalyzeResponse:
        """
        Parse raw AI output and return a MacroAnalyzeResponse.

        Args:
            raw_text: The raw string response from the AI provider.
            symbol: The trading symbol.
            news_articles: List of fetched news article dicts.
            calendar_events: List of fetched calendar event dicts.
            provider_used: Provider name (vertex/openai).
            model_used: Model identifier.

        Returns:
            MacroAnalyzeResponse with processed fields.
        """
        parsed = safe_json_parse(raw_text) or {}

        sentiment = parsed.get("sentiment", "neutral")
        if sentiment not in ("bullish", "bearish", "neutral"):
            sentiment = "neutral"

        key_factors = []
        for kf in parsed.get("key_factors", []):
            try:
                key_factors.append(KeyFactor(
                    factor=kf.get("factor", ""),
                    impact=kf.get("impact", ""),
                    probability=float(kf.get("probability", 0.5)),
                ))
            except Exception:
                pass

        news_models = []
        for a in news_articles[:5]:
            try:
                news_models.append(NewsArticle(
                    title=a.get("title", ""),
                    source=a.get("source", "Unknown"),
                    time=a.get("time", ""),
                    url=a.get("url"),
                    sentiment=a.get("sentiment"),
                ))
            except Exception:
                pass

        calendar_models = []
        for ev in calendar_events[:5]:
            try:
                impact = ev.get("impact", "medium")
                if impact not in ("low", "medium", "high"):
                    impact = "medium"
                calendar_models.append(CalendarEvent(
                    event=ev.get("event", ""),
                    date=ev.get("date", ""),
                    forecast=ev.get("forecast"),
                    previous=ev.get("previous"),
                    impact=impact,
                ))
            except Exception:
                pass

        return MacroAnalyzeResponse(
            id=f"macro_{uuid.uuid4().hex[:8]}",
            symbol=symbol,
            timestamp=now_ts(),
            summary=parsed.get("summary", raw_text[:300] if raw_text else "Analysis unavailable."),
            sentiment=sentiment,
            confidence=min(max(float(parsed.get("confidence", 0.6)), 0.0), 1.0),
            key_factors=key_factors,
            news=news_models,
            calendar_events=calendar_models,
            historical_reaction=parsed.get("historical_reaction"),
            sources=parsed.get("sources", []),
            provider_used=provider_used,
            model_used=model_used,
            processing_time_ms=0,  # filled by route
        )
