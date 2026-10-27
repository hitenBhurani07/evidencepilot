"""Base protocols, models, and sanitized exceptions for external providers."""

from __future__ import annotations

from typing import Any, List, Optional, Protocol, Type, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T", bound=BaseModel)


# ---------------------------------------------------------------------------
# Sanitized Provider Exceptions (never print raw keys in error strings)
# ---------------------------------------------------------------------------

class ProviderError(Exception):
    """Base exception for provider failures."""
    
    def __init__(self, message: str, provider_name: str = "unknown", status_code: Optional[int] = None):
        super().__init__(f"[{provider_name}] {message}")
        self.provider_name = provider_name
        self.status_code = status_code


class AuthError(ProviderError):
    """Raised when provider rejects credentials (e.g. 401 or 403)."""
    pass


class RateLimitError(ProviderError):
    """Raised when quota or rate limit is reached (e.g. 429)."""
    pass


class NetworkError(ProviderError):
    """Raised on connection timeout or network level failures."""
    pass


class ContentFilterError(ProviderError):
    """Raised if safety filters or content moderation block the request/response."""
    pass


class SchemaValidationError(ProviderError):
    """Raised when model response cannot be parsed into the expected Pydantic schema."""
    pass


# ---------------------------------------------------------------------------
# Provider Output Models
# ---------------------------------------------------------------------------

class SearchResult(BaseModel):
    """Raw search result item returned from a search provider."""
    
    url: str = Field(..., description="Target webpage URL")
    title: str = Field(default="", description="Result title")
    snippet: str = Field(default="", description="Search snippet or summary excerpt")
    raw_content: Optional[str] = Field(default=None, description="Optional page body if provided by search engine")
    score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Provider relevance score")


# ---------------------------------------------------------------------------
# Protocols (Interfaces)
# ---------------------------------------------------------------------------

class LLMProvider(Protocol):
    """Interface for LLM text and structured output generation."""
    
    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Generate freeform text."""
        ...

    def generate_structured(
        self,
        prompt: str,
        schema_class: Type[T],
        system_instruction: Optional[str] = None,
    ) -> T:
        """Generate structured output validated against a Pydantic schema."""
        ...


class SearchProvider(Protocol):
    """Interface for web search providers."""
    
    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """Execute a search query and return normalized results."""
        ...
