"""
Context builder for gas-rag-macro RAG pipeline.
Assembles the final prompt from retrieved news, calendar, price data, and vector docs.
"""
from __future__ import annotations
from typing import Any

from src.lib.utils import truncate_text

SYSTEM_PROMPT = """You are an expert macroeconomic analyst specializing in financial markets.
You analyze macroeconomic data, news sentiment, and economic calendar events to provide
actionable insights for traders. Your analysis is data-driven, concise, and structured.

Always respond in the following JSON format:
{
  "summary": "<concise 2-3 sentence macro outlook>",
  "sentiment": "<bullish|bearish|neutral>",
  "confidence": <float 0.0–1.0>,
  "key_factors": [
    {"factor": "<name>", "impact": "<description>", "probability": <float>}
  ],
  "historical_reaction": "<how asset reacted historically to similar events>",
  "sources": ["<source1>", "<source2>"]
}"""


def _format_news(articles: list[dict]) -> str:
    if not articles:
        return "No news available."
    lines = []
    for a in articles[:8]:
        title = truncate_text(a.get("title", ""), 150)
        source = a.get("source", "Unknown")
        time_str = a.get("time", "")
        lines.append(f"- [{source}] {title} ({time_str})")
    return "\n".join(lines)


def _format_calendar(events: list[dict]) -> str:
    if not events:
        return "No upcoming events."
    lines = []
    for ev in events[:6]:
        name = ev.get("event", "")
        date = ev.get("date", "")
        impact = ev.get("impact", "medium").upper()
        forecast = ev.get("forecast", "N/A")
        previous = ev.get("previous", "N/A")
        lines.append(f"- [{impact}] {name} on {date} | Forecast: {forecast} | Previous: {previous}")
    return "\n".join(lines)


def _format_price_data(price_data: dict | None) -> str:
    if not price_data:
        return "Price data unavailable."
    symbol = price_data.get("symbol", "")
    close = price_data.get("close", "N/A")
    change = price_data.get("change_pct", "N/A")
    high = price_data.get("high", "N/A")
    low = price_data.get("low", "N/A")
    return f"Symbol: {symbol} | Close: {close} | Change: {change}% | High: {high} | Low: {low}"


def _format_retrieved_docs(docs: list[dict]) -> str:
    if not docs:
        return "No relevant historical context found."
    parts = []
    for i, doc in enumerate(docs[:4], 1):
        content = truncate_text(doc.get("content", ""), 500)
        parts.append(f"[Doc {i}] {content}")
    return "\n\n".join(parts)


class ContextBuilder:
    """Assembles the full prompt for the AI model."""

    def build(
        self,
        query: str,
        symbol: str,
        time_horizon: str,
        news_articles: list[dict],
        calendar_events: list[dict],
        price_data: dict | None,
        retrieved_docs: list[dict],
    ) -> tuple[str, str]:
        """
        Build (system_prompt, user_prompt) tuple.

        Returns:
            Tuple of (system_prompt, user_prompt).
        """
        user_prompt = f"""Analyze the macroeconomic outlook for {symbol} over the next {time_horizon}.

USER QUERY: {query}

=== LATEST NEWS ===
{_format_news(news_articles)}

=== ECONOMIC CALENDAR (Upcoming Events) ===
{_format_calendar(calendar_events)}

=== CURRENT MARKET DATA ===
{_format_price_data(price_data)}

=== HISTORICAL MACRO CONTEXT ===
{_format_retrieved_docs(retrieved_docs)}

Based on all the above, provide your macroeconomic analysis in the specified JSON format."""

        return SYSTEM_PROMPT, user_prompt
