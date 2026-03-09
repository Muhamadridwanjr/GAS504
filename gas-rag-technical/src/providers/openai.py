"""
OpenAI provider implementation.
Supports GPT-4o, GPT-4 Turbo, and text-embedding-3-small/large.
"""
from typing import Any
import openai
from src.config import settings
from src.providers.base import BaseProvider
from src.core.exceptions import ProviderError
from src.lib.logger import get_logger

logger = get_logger(__name__)


class OpenAIProvider(BaseProvider):
    """Wraps OpenAI Async client for chat completions and embeddings."""

    def __init__(self) -> None:
        if not settings.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not set – OpenAI provider will fail at runtime.")
        self._client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY or "dummy")
        self._model = settings.OPENAI_MODEL
        self._embedding_model = settings.OPENAI_EMBEDDING_MODEL

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return self._model

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        params: dict[str, Any] | None = None,
    ) -> str:
        params = params or {}
        try:
            response = await self._client.chat.completions.create(
                model=params.get("model", self._model),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=params.get("temperature", 0.3),
                max_tokens=params.get("max_tokens", 1500),
            )
            return response.choices[0].message.content or ""
        except openai.OpenAIError as exc:
            raise ProviderError(f"OpenAI generation failed: {exc}") from exc

    async def get_embedding(self, text: str) -> list[float]:
        try:
            response = await self._client.embeddings.create(
                model=self._embedding_model,
                input=text,
            )
            return response.data[0].embedding
        except openai.OpenAIError as exc:
            raise ProviderError(f"OpenAI embedding failed: {exc}") from exc
