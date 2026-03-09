"""
OpenAI provider for gas-rag-macro.
Uses GPT-4o via the official openai SDK.
"""
from __future__ import annotations

from openai import AsyncOpenAI

from src.config import settings
from src.providers.base import BaseProvider
from src.lib.logger import get_logger

logger = get_logger(__name__)


class OpenAIProvider(BaseProvider):
    """OpenAI (GPT-4o) provider implementation."""

    def __init__(self):
        self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

    @property
    def name(self) -> str:
        return "openai"

    @property
    def model(self) -> str:
        return settings.OPENAI_MODEL

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 1200,
    ) -> str:
        if not self._client:
            raise RuntimeError("OpenAI API key not configured")

        logger.info("openai.generate", model=settings.OPENAI_MODEL)
        response = await self._client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content or ""
