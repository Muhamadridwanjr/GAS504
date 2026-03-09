"""
Vertex AI (Gemini) provider for gas-rag-macro.
Uses google-generativeai SDK.
"""
from __future__ import annotations

from src.config import settings
from src.providers.base import BaseProvider
from src.lib.logger import get_logger

logger = get_logger(__name__)


class VertexProvider(BaseProvider):
    """Vertex AI (Gemini) provider implementation."""

    def __init__(self):
        self._available = bool(
            settings.VERTEX_PROJECT_ID and settings.GOOGLE_APPLICATION_CREDENTIALS
        )
        self._model = None
        if self._available:
            self._init_client()

    def _init_client(self):
        try:
            import google.generativeai as genai
            import google.auth
            import os

            os.environ.setdefault(
                "GOOGLE_APPLICATION_CREDENTIALS", settings.GOOGLE_APPLICATION_CREDENTIALS
            )
            credentials, _ = google.auth.default(
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            genai.configure(credentials=credentials)
            self._model = genai.GenerativeModel(settings.VERTEX_MODEL)
            logger.info("vertex.client.initialized", model=settings.VERTEX_MODEL)
        except Exception as exc:
            logger.warning("vertex.client.init_failed", error=str(exc))
            self._available = False

    @property
    def name(self) -> str:
        return "vertex"

    @property
    def model(self) -> str:
        return settings.VERTEX_MODEL

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 1200,
    ) -> str:
        if not self._available or not self._model:
            raise RuntimeError("Vertex AI not configured or unavailable")

        import asyncio

        logger.info("vertex.generate", model=settings.VERTEX_MODEL)

        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }

        # Run sync SDK in thread pool
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self._model.generate_content(
                full_prompt,
                generation_config=generation_config,
            ),
        )
        return response.text or ""
