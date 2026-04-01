"""
GAS Agent Engine — Model Router
Routes AI inference requests to the optimal model based on task type,
user subscription tier, and model availability (circuit breaker).
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import time
from typing import Any, Optional

import httpx
import redis.asyncio as aioredis
from anthropic import AsyncAnthropic

import config

logger = logging.getLogger(__name__)


# ─── Task-to-model routing policy ─────────────────────────────────────────────
# Maps feature/task types to preferred model tier.
# 'complex' → claude-sonnet-4-6
# 'fast'    → claude-haiku-4-5-20251001
# 'local'   → Ollama local model
ROUTING_POLICY: dict[str, str] = {
    # Complex multi-step reasoning — sonnet
    "psychology": "complex",
    "mentor": "complex",
    "market_briefing": "complex",
    "strategy_validation": "complex",
    "backtest_analysis": "complex",
    "trade_planning": "complex",
    "rag_synthesis": "complex",
    "context_synthesis": "complex",
    # Fast feature-specific tasks — haiku
    "technical": "fast",
    "signal_explanation": "fast",
    "pattern_summary": "fast",
    "regime_summary": "fast",
    "fundamental": "fast",
    "calendar": "fast",
    "sentiment": "fast",
    "risk_summary": "fast",
    "alert_formatting": "fast",
    "screener": "fast",
    # Local/private — ollama
    "journal_analysis": "local",
    "performance_analysis": "local",
}


class ModelRouter:
    """
    Routes AI inference to the appropriate model tier based on task type.
    Implements circuit breaker pattern, response caching, and fallback routing.
    """

    def __init__(self) -> None:
        self._anthropic: Optional[AsyncAnthropic] = None
        self._http: Optional[httpx.AsyncClient] = None
        self._redis: Optional[aioredis.Redis] = None

    # ─── Lifecycle ────────────────────────────────────────────────────────────

    async def startup(self) -> None:
        self._anthropic = AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY)
        self._http = httpx.AsyncClient(timeout=60.0, follow_redirects=True)
        self._redis = aioredis.from_url(
            config.REDIS_URL,
            max_connections=5,
            decode_responses=True,
        )
        logger.info("ModelRouter started")

    async def shutdown(self) -> None:
        if self._http:
            await self._http.aclose()
        if self._redis:
            await self._redis.aclose()
        if self._anthropic:
            await self._anthropic.close()

    # ─── Public API ───────────────────────────────────────────────────────────

    async def route(
        self,
        task_type: str,
        prompt: str,
        context: str = "",
        system_prompt: Optional[str] = None,
        user_plan: str = "essential",
        max_tokens: Optional[int] = None,
        cache_ttl: int = 300,
    ) -> dict[str, Any]:
        """
        Route an inference request to the best available model.
        Returns dict with keys: response, model_used, tokens_in, tokens_out, latency_ms, cached
        """
        # Check response cache first
        if config.ENABLE_RESPONSE_CACHE:
            cache_key = self._cache_key(task_type, prompt, context)
            cached = await self._get_cached_response(cache_key)
            if cached:
                logger.debug("ModelRouter cache hit for task '%s'", task_type)
                return {**cached, "cached": True}

        # Select model tier
        model_id = self._select_model(task_type, user_plan)

        # Check circuit breaker
        if config.ENABLE_CIRCUIT_BREAKER:
            if await self._is_circuit_open(model_id):
                logger.warning("Circuit open for %s — falling back", model_id)
                model_id = self._fallback_model(model_id)

        # Build messages
        messages = self._build_messages(prompt, context)
        _system = system_prompt or self._default_system_prompt(task_type)

        # Execute inference
        start = time.monotonic()
        try:
            if model_id.startswith("claude"):
                result = await self.call_claude(model_id, messages, _system, max_tokens)
            else:
                result = await self.call_local(prompt, context, model_id)

            latency_ms = round((time.monotonic() - start) * 1000, 1)
            await self._record_success(model_id)

            response_obj = {
                "response": result["content"],
                "model_used": model_id,
                "tokens_in": result.get("tokens_in", 0),
                "tokens_out": result.get("tokens_out", 0),
                "latency_ms": latency_ms,
                "cached": False,
            }

            # Cache the response
            if config.ENABLE_RESPONSE_CACHE and cache_ttl > 0:
                await self._cache_response(cache_key, response_obj, ttl=cache_ttl)

            # Track usage
            await self._track_usage(model_id, result.get("tokens_in", 0), result.get("tokens_out", 0))

            return response_obj

        except Exception as exc:
            latency_ms = round((time.monotonic() - start) * 1000, 1)
            await self._record_failure(model_id)
            logger.error("ModelRouter inference error [%s]: %s", model_id, exc, exc_info=True)
            raise

    def select_model(self, task_type: str, user_plan: str = "essential") -> str:
        """
        Determine the best model ID for the given task type and user plan.
        Essential/Plus users are capped at fast model to control costs.
        """
        return self._select_model(task_type, user_plan)

    async def call_claude(
        self,
        model: str,
        messages: list[dict[str, str]],
        system: str = "",
        max_tokens: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Call Anthropic Claude API with the given messages.
        Returns dict with content, tokens_in, tokens_out.
        """
        _max_tokens = max_tokens or (
            config.MODEL_COMPLEX_MAX_TOKENS
            if "sonnet" in model
            else config.MODEL_FAST_MAX_TOKENS
        )
        response = await self._anthropic.messages.create(
            model=model,
            max_tokens=_max_tokens,
            system=system,
            messages=messages,
        )
        content = response.content[0].text if response.content else ""
        return {
            "content": content,
            "tokens_in": response.usage.input_tokens,
            "tokens_out": response.usage.output_tokens,
            "stop_reason": response.stop_reason,
        }

    async def call_local(
        self,
        prompt: str,
        context: str = "",
        model: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Call local Ollama model for privacy-sensitive or low-latency tasks.
        Returns dict with content (no token counts for local models).
        """
        if not config.ENABLE_LOCAL_MODEL:
            raise RuntimeError("Local model is disabled — set ENABLE_LOCAL_MODEL=true")

        _model = model or config.MODEL_LOCAL
        full_prompt = f"{context}\n\n{prompt}" if context else prompt

        payload = {
            "model": _model,
            "prompt": full_prompt,
            "stream": False,
        }
        try:
            response = await self._http.post(
                f"{config.OLLAMA_BASE_URL}/api/generate",
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            return {
                "content": data.get("response", ""),
                "tokens_in": data.get("prompt_eval_count", 0),
                "tokens_out": data.get("eval_count", 0),
            }
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Ollama call failed: {exc}") from exc

    # ─── Private Helpers ──────────────────────────────────────────────────────

    def _select_model(self, task_type: str, user_plan: str) -> str:
        tier = ROUTING_POLICY.get(task_type, "fast")

        # Downgrade plan-based users from complex to fast
        if tier == "complex" and user_plan in ("essential", "plus"):
            tier = "fast"

        # Downgrade to local if feature flag set
        if tier == "local" and not config.ENABLE_LOCAL_MODEL:
            tier = "fast"

        model_map = {
            "complex": config.MODEL_COMPLEX,
            "fast": config.MODEL_FAST,
            "local": config.MODEL_LOCAL,
        }
        return model_map.get(tier, config.MODEL_FAST)

    def _fallback_model(self, primary_model: str) -> str:
        """Return the next fallback model when circuit breaker is open."""
        if primary_model == config.MODEL_COMPLEX:
            return config.MODEL_FAST
        if primary_model == config.MODEL_FAST and config.ENABLE_LOCAL_MODEL:
            return config.MODEL_LOCAL
        raise RuntimeError(f"No fallback available for model: {primary_model}")

    def _build_messages(self, prompt: str, context: str) -> list[dict[str, str]]:
        """Construct the messages array for the Claude API."""
        if context:
            user_content = f"<context>\n{context}\n</context>\n\n{prompt}"
        else:
            user_content = prompt
        return [{"role": "user", "content": user_content}]

    def _default_system_prompt(self, task_type: str) -> str:
        """Return a default system prompt based on task type."""
        prompts = {
            "technical": "You are a professional technical analyst specializing in forex and crypto markets.",
            "psychology": "You are an expert trading psychologist helping traders improve their mental edge.",
            "mentor": "You are a seasoned trading mentor with decades of market experience.",
            "market_briefing": "You are a market analyst preparing a professional daily briefing.",
            "risk_summary": "You are a risk manager summarizing portfolio exposure in clear terms.",
        }
        return prompts.get(
            task_type,
            "You are GAS AI, an advanced trading intelligence assistant."
        )

    def _cache_key(self, task_type: str, prompt: str, context: str) -> str:
        """Generate a deterministic cache key for a request."""
        raw = f"{task_type}::{prompt[:200]}::{context[:200]}"
        return "ai:response_cache:" + hashlib.sha256(raw.encode()).hexdigest()[:16]

    async def _get_cached_response(self, cache_key: str) -> Optional[dict[str, Any]]:
        try:
            raw = await self._redis.get(cache_key)
            if raw:
                return json.loads(raw)
        except Exception:
            pass
        return None

    async def _cache_response(
        self, cache_key: str, response: dict[str, Any], ttl: int = 300
    ) -> None:
        try:
            await self._redis.set(cache_key, json.dumps(response), ex=ttl)
        except Exception as exc:
            logger.warning("ModelRouter cache write failed: %s", exc)

    async def _is_circuit_open(self, model_id: str) -> bool:
        """Check if the circuit breaker is open for this model."""
        key = f"ai:circuit_breaker:{model_id}"
        try:
            return bool(await self._redis.exists(key))
        except Exception:
            return False

    async def _record_success(self, model_id: str) -> None:
        """Reset failure counter on successful inference."""
        key = f"ai:failures:{model_id}"
        try:
            await self._redis.delete(key)
        except Exception:
            pass

    async def _record_failure(self, model_id: str) -> None:
        """Increment failure counter; open circuit if threshold reached."""
        key = f"ai:failures:{model_id}"
        try:
            count = await self._redis.incr(key)
            await self._redis.expire(key, 600)  # Reset window: 10 minutes
            if count >= config.CIRCUIT_BREAKER_THRESHOLD:
                cb_key = f"ai:circuit_breaker:{model_id}"
                await self._redis.set(cb_key, "1", ex=config.CIRCUIT_BREAKER_TIMEOUT)
                logger.error(
                    "Circuit breaker OPENED for model %s after %d failures",
                    model_id, count,
                )
        except Exception as exc:
            logger.warning("ModelRouter failure tracking error: %s", exc)

    async def _track_usage(self, model_id: str, tokens_in: int, tokens_out: int) -> None:
        """Record token usage in Redis for daily budget tracking."""
        date_key = time.strftime("%Y-%m-%d")
        key = f"ai:usage:{model_id}:{date_key}"
        try:
            pipe = self._redis.pipeline()
            pipe.hincrby(key, "tokens_in", tokens_in)
            pipe.hincrby(key, "tokens_out", tokens_out)
            pipe.hincrby(key, "calls", 1)
            pipe.expire(key, 7 * 24 * 3600)  # Keep 7 days
            await pipe.execute()
        except Exception as exc:
            logger.warning("ModelRouter usage tracking error: %s", exc)

    async def get_usage_today(self) -> dict[str, dict[str, int]]:
        """Return today's token usage per model."""
        date_key = time.strftime("%Y-%m-%d")
        usage = {}
        for model_id in [config.MODEL_COMPLEX, config.MODEL_FAST, config.MODEL_LOCAL]:
            key = f"ai:usage:{model_id}:{date_key}"
            try:
                data = await self._redis.hgetall(key)
                usage[model_id] = {
                    "tokens_in": int(data.get("tokens_in", 0)),
                    "tokens_out": int(data.get("tokens_out", 0)),
                    "calls": int(data.get("calls", 0)),
                }
            except Exception:
                usage[model_id] = {"tokens_in": 0, "tokens_out": 0, "calls": 0}
        return usage
