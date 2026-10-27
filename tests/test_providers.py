"""Unit tests for provider adapters, fakes, and sanitized error mapping."""

import pytest
from unittest.mock import MagicMock, patch
from pydantic import BaseModel

from evidencepilot.providers.base import (
    AuthError,
    ContentFilterError,
    NetworkError,
    ProviderError,
    RateLimitError,
    SchemaValidationError,
    SearchResult,
)
from evidencepilot.providers.fakes import FakeLLMProvider, FakeSearchProvider
from evidencepilot.providers.gemini import GeminiProvider
from evidencepilot.providers.tavily import TavilySearchProvider
from evidencepilot.schemas.research import ResearchPlan, StructuredAnswer


class SimpleTestSchema(BaseModel):
    message: str
    count: int


def test_fake_llm_provider_text_and_structured():
    fake = FakeLLMProvider(default_text="Hello Antigravity")
    assert fake.generate_text("Hi") == "Hello Antigravity"
    assert len(fake.call_history) == 1

    # Default auto-generation for known schema
    plan = fake.generate_structured("Plan query", ResearchPlan)
    assert isinstance(plan, ResearchPlan)
    assert plan.question == "Sample Question"
    assert len(plan.steps) >= 1

    # Custom structured response
    custom_fake = FakeLLMProvider(
        structured_responses={"SimpleTestSchema": SimpleTestSchema(message="OK", count=42)}
    )
    res = custom_fake.generate_structured("give me schema", SimpleTestSchema)
    assert res.message == "OK"
    assert res.count == 42


def test_fake_search_provider():
    fake = FakeSearchProvider()
    results = fake.search("test query", max_results=1)
    assert len(results) == 1
    assert "wikipedia" in results[0].url.lower()

    # Query specific override
    custom_fake = FakeSearchProvider(
        query_responses={"custom": [SearchResult(url="https://custom.org", title="Custom", snippet="Snippet")]}
    )
    custom_results = custom_fake.search("custom")
    assert len(custom_results) == 1
    assert custom_results[0].url == "https://custom.org"


def test_gemini_provider_init_and_sanitization():
    # Empty key raises AuthError
    with pytest.raises(AuthError):
        GeminiProvider(api_key="")

    with pytest.raises(AuthError):
        GeminiProvider(api_key="   ")

    provider = GeminiProvider(api_key="AIzaSyTestSecretKey12345")
    assert provider.model_name == "gemini-2.5-flash"

    # Verify exception mapping redacts key
    raw_error = Exception("API error with key AIzaSyTestSecretKey12345: 403 Forbidden")
    mapped = provider._map_exception(raw_error)
    assert isinstance(mapped, AuthError)
    assert "AIzaSyTestSecretKey12345" not in str(mapped)
    assert "[REDACTED_API_KEY]" in str(mapped)


def test_gemini_provider_parse_and_validate():
    provider = GeminiProvider(api_key="AIzaSyTestSecretKey12345")

    # Valid JSON string
    valid_json = '{"message": "success", "count": 10}'
    result = provider._parse_and_validate(valid_json, SimpleTestSchema)
    assert result.message == "success"
    assert result.count == 10

    # Markdown code fence JSON
    fence_json = '```json\n{"message": "fenced", "count": 20}\n```'
    result2 = provider._parse_and_validate(fence_json, SimpleTestSchema)
    assert result2.message == "fenced"
    assert result2.count == 20

    # Malformed JSON raises SchemaValidationError
    with pytest.raises(SchemaValidationError) as exc_malformed:
        provider._parse_and_validate('{"incomplete": ', SimpleTestSchema)
    assert "Failed to parse JSON" in str(exc_malformed.value)

    # Missing schema field raises SchemaValidationError
    with pytest.raises(SchemaValidationError) as exc_validation:
        provider._parse_and_validate('{"message": "only_message"}', SimpleTestSchema)
    assert "failed Pydantic schema validation" in str(exc_validation.value)


def test_tavily_search_provider_init_and_empty_query():
    with pytest.raises(AuthError):
        TavilySearchProvider(api_key="")

    provider = TavilySearchProvider(api_key="tvly-secretkey123")
    assert provider.search("") == []
    assert provider.search("   ") == []


@patch("httpx.Client.post")
def test_tavily_search_provider_success(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "results": [
            {
                "url": "https://example.com/ai",
                "title": "AI Overview",
                "content": "AI is advancing rapidly.",
                "score": 0.92,
            },
            # Malformed item without URL (should be gracefully skipped)
            {
                "title": "No URL item",
                "content": "Missing URL item",
            }
        ]
    }
    mock_post.return_value = mock_resp

    provider = TavilySearchProvider(api_key="tvly-secretkey123")
    results = provider.search("AI advances")

    assert len(results) == 1
    assert results[0].url == "https://example.com/ai"
    assert results[0].title == "AI Overview"
    assert results[0].score == 0.92


@patch("httpx.Client.post")
def test_tavily_search_provider_auth_error(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_post.return_value = mock_resp

    provider = TavilySearchProvider(api_key="tvly-invalid-key")
    with pytest.raises(AuthError) as exc:
        provider.search("test")
    assert "Authentication failed" in str(exc.value)
    assert "tvly-invalid-key" not in str(exc.value)


@patch("httpx.Client.post")
def test_tavily_search_provider_rate_limit(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 429
    mock_post.return_value = mock_resp

    provider = TavilySearchProvider(api_key="tvly-key")
    with pytest.raises(RateLimitError) as exc:
        provider.search("test")
    assert "rate limit or monthly credit quota exceeded" in str(exc.value)
