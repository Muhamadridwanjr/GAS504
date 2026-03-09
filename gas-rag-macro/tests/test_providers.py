"""
Provider routing tests for gas-rag-macro.
"""
import pytest
from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_provider_router_uses_preferred():
    from src.providers.router import ProviderRouter

    router = ProviderRouter()
    router._providers["openai"] = AsyncMock()
    router._providers["openai"].generate = AsyncMock(return_value='{"summary":"test"}')
    router._providers["openai"].name = "openai"
    router._providers["openai"].model = "gpt-4o"
    router._providers["vertex"] = AsyncMock()
    router._providers["vertex"].generate = AsyncMock(return_value='{"summary":"vertex"}')
    router._providers["vertex"].name = "vertex"
    router._providers["vertex"].model = "gemini-1.5-pro"

    text, provider, model = await router.generate(
        system_prompt="sys",
        user_prompt="usr",
        provider_preference="openai",
    )
    assert provider == "openai"
    assert text == '{"summary":"test"}'


@pytest.mark.asyncio
async def test_provider_router_fallback():
    from src.providers.router import ProviderRouter

    router = ProviderRouter()
    # Primary fails
    router._providers["openai"] = AsyncMock()
    router._providers["openai"].generate = AsyncMock(side_effect=RuntimeError("API error"))
    router._providers["openai"].name = "openai"
    router._providers["openai"].model = "gpt-4o"
    # Fallback succeeds
    router._providers["vertex"] = AsyncMock()
    router._providers["vertex"].generate = AsyncMock(return_value='{"summary":"fallback"}')
    router._providers["vertex"].name = "vertex"
    router._providers["vertex"].model = "gemini-1.5-pro"

    text, provider, model = await router.generate(
        system_prompt="sys",
        user_prompt="usr",
        provider_preference="openai",
    )
    assert provider == "vertex"
    assert "fallback" in text


@pytest.mark.asyncio
async def test_provider_router_all_fail():
    from src.providers.router import ProviderRouter

    router = ProviderRouter()
    for name in ["openai", "vertex"]:
        mock = AsyncMock()
        mock.generate = AsyncMock(side_effect=RuntimeError("fail"))
        router._providers[name] = mock

    with pytest.raises(RuntimeError, match="All providers failed"):
        await router.generate(system_prompt="sys", user_prompt="usr")
