"""Tavily search provider adapter using official REST API."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import httpx
from pydantic import ValidationError

from evidencepilot.providers.base import (
    AuthError,
    NetworkError,
    ProviderError,
    RateLimitError,
    SearchResult,
)


class TavilySearchProvider:
    """Production adapter for Tavily AI Search API."""
    
    API_URL = "https://api.tavily.com/search"

    def __init__(self, api_key: str, timeout_seconds: float = 15.0):
        if not api_key or not api_key.strip():
            raise AuthError("Tavily API key cannot be empty", provider_name="tavily")
        self.api_key = api_key.strip()
        self.timeout_seconds = timeout_seconds

    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """Execute web search and return sanitized, normalized SearchResult items."""
        cleaned_query = query.strip()
        if not cleaned_query:
            return []

        payload: Dict[str, Any] = {
            "api_key": self.api_key,
            "query": cleaned_query,
            "search_depth": "basic",
            "max_results": max(1, min(max_results, 10)),
            "include_answer": False,
            "include_raw_content": False,
        }

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(
                    self.API_URL,
                    json=payload,
                    headers={"Accept": "application/json"}
                )
        except httpx.TimeoutException as exc:
            raise NetworkError(f"Search request timed out after {self.timeout_seconds}s", provider_name="tavily") from exc
        except httpx.RequestError as exc:
            raise NetworkError(f"Network error connecting to search provider: {exc}", provider_name="tavily") from exc

        if response.status_code in (401, 403):
            raise AuthError(
                "Authentication failed: Invalid Tavily API key or permissions rejected.",
                provider_name="tavily",
                status_code=response.status_code,
            )
        if response.status_code == 429:
            raise RateLimitError(
                "Tavily rate limit or monthly credit quota exceeded.",
                provider_name="tavily",
                status_code=429,
            )
        if response.status_code >= 400:
            raise ProviderError(
                f"Tavily search API error (HTTP {response.status_code})",
                provider_name="tavily",
                status_code=response.status_code,
            )

        try:
            data = response.json()
        except Exception as exc:
            raise ProviderError("Failed to decode JSON from Tavily response", provider_name="tavily") from exc

        raw_results = data.get("results", [])
        results: List[SearchResult] = []
        for item in raw_results:
            try:
                url = item.get("url")
                if not url or not isinstance(url, str):
                    continue
                results.append(
                    SearchResult(
                        url=url.strip(),
                        title=str(item.get("title", "")).strip(),
                        snippet=str(item.get("content", "")).strip(),
                        score=float(item["score"]) if "score" in item and item["score"] is not None else None,
                    )
                )
            except (ValidationError, ValueError, TypeError):
                # Skip individual malformed result items gracefully
                continue

        return results
