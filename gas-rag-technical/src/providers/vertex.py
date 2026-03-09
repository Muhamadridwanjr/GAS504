"""
Vertex AI provider implementation.
Uses Gemini models via Google Cloud Vertex AI.
"""
from typing import Any
from src.config import settings
from src.providers.base import BaseProvider
from src.core.exceptions import ProviderError
from src.lib.logger import get_logger

logger = get_logger(__name__)


class VertexProvider(BaseProvider):
    """Wraps Vertex AI Gemini for text generation and embeddings."""

    def __init__(self) -> None:
        self._model_name = settings.VERTEX_MODEL
        self._embedding_model = settings.VERTEX_EMBEDDING_MODEL
        self._initialized = False
        try:
            import vertexai
            from vertexai.generative_models import GenerativeModel  # noqa: F401
            vertexai.init(
                project=settings.VERTEX_PROJECT_ID,
                location=settings.VERTEX_LOCATION,
            )
            self._initialized = True
            logger.info("Vertex AI initialized (project=%s)", settings.VERTEX_PROJECT_ID)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Vertex AI init failed (will fail at runtime): %s", exc)

    @property
    def provider_name(self) -> str:
        return "vertex"

    @property
    def model_name(self) -> str:
        return self._model_name

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        params: dict[str, Any] | None = None,
    ) -> str:
        if not self._initialized:
            raise ProviderError("Vertex AI is not initialized – check credentials.")
        params = params or {}
        try:
            import asyncio
            from vertexai.generative_models import GenerativeModel, GenerationConfig

            model = GenerativeModel(
                model_name=params.get("model", self._model_name),
                system_instruction=system_prompt,
            )
            config = GenerationConfig(
                temperature=params.get("temperature", 0.3),
                max_output_tokens=params.get("max_tokens", 1500),
            )
            # Vertex SDK is sync; run in executor to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: model.generate_content(user_prompt, generation_config=config),
            )
            return response.text
        except Exception as exc:  # noqa: BLE001
            raise ProviderError(f"Vertex AI generation failed: {exc}") from exc

    async def get_embedding(self, text: str) -> list[float]:
        if not self._initialized:
            raise ProviderError("Vertex AI is not initialized.")
        try:
            import asyncio
            from vertexai.language_models import TextEmbeddingModel

            emb_model = TextEmbeddingModel.from_pretrained(self._embedding_model)
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None, lambda: emb_model.get_embeddings([text])
            )
            return embeddings[0].values
        except Exception as exc:  # noqa: BLE001
            raise ProviderError(f"Vertex AI embedding failed: {exc}") from exc
