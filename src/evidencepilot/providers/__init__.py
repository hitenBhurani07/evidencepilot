"""Provider adapters and abstractions for LLM and Search services."""

from evidencepilot.providers.base import (
    AuthError,
    ContentFilterError,
    LLMProvider,
    NetworkError,
    ProviderError,
    RateLimitError,
    SchemaValidationError,
    SearchProvider,
    SearchResult,
)
from evidencepilot.providers.fakes import FakeLLMProvider, FakeSearchProvider
from evidencepilot.providers.gemini import GeminiProvider
from evidencepilot.providers.tavily import TavilySearchProvider

__all__ = [
    "ProviderError",
    "AuthError",
    "RateLimitError",
    "NetworkError",
    "ContentFilterError",
    "SchemaValidationError",
    "SearchResult",
    "LLMProvider",
    "SearchProvider",
    "FakeLLMProvider",
    "FakeSearchProvider",
    "GeminiProvider",
    "TavilySearchProvider",
]
