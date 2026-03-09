"""Tests for provider routing logic."""
import pytest
from unittest.mock import patch, MagicMock


def test_router_returns_openai_by_default():
    """Router should return OpenAI provider when default is 'openai'."""
    with patch("src.providers.router.settings") as mock_settings:
        mock_settings.DEFAULT_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = "sk-test"
        mock_settings.VERTEX_PROJECT_ID = ""

        from src.providers.router import ProviderRouter
        router = ProviderRouter()
        provider = router.get_provider()
        assert provider.provider_name == "openai"


def test_router_falls_back_to_openai_when_vertex_unconfigured():
    """Router should fall back to OpenAI if Vertex credentials are missing."""
    with patch("src.providers.router.settings") as mock_settings:
        mock_settings.VERTEX_PROJECT_ID = ""
        mock_settings.OPENAI_API_KEY = "sk-test"
        mock_settings.DEFAULT_PROVIDER = "openai"

        from src.providers.router import ProviderRouter
        router = ProviderRouter()
        provider = router.get_provider("vertex")
        # Falls back because no project ID
        assert provider.provider_name == "openai"


def test_response_parser_handles_valid_json():
    """Parser should correctly parse a valid JSON string."""
    from src.core.response_parser import parse_response

    raw = '{"summary":"Bullish","key_levels":{"support":[1990],"resistance":[2010]},"signal":"BUY","confidence":0.8,"entry":{"price":2005,"stop_loss":1985,"take_profit":[2020]},"reasoning":"Test","short_term_bias":"bullish","key_risks":[]}'
    result = parse_response(raw)
    assert result["signal"] == "BUY"
    assert result["confidence"] == 0.8
    assert result["key_levels"]["support"] == [1990]


def test_response_parser_handles_fenced_json():
    """Parser should extract JSON from markdown code fences."""
    from src.core.response_parser import parse_response

    raw = '''Here is the analysis:
```json
{"summary":"Test","key_levels":{"support":[],"resistance":[]},"signal":"NEUTRAL","confidence":0.5,"entry":{"price":null,"stop_loss":null,"take_profit":[]},"reasoning":"No clear signal","short_term_bias":"sideways","key_risks":[]}
```'''
    result = parse_response(raw)
    assert result["signal"] == "NEUTRAL"


def test_response_parser_fallback_on_garbage():
    """Parser should not raise even on completely garbled output."""
    from src.core.response_parser import parse_response

    result = parse_response("This is definitely not JSON at all lol")
    assert "signal" in result
    assert "summary" in result
