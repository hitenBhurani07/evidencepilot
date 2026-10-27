"""Deterministic test fakes for LLM and Search providers."""

from __future__ import annotations

import json
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar
from pydantic import BaseModel
from evidencepilot.providers.base import (
    AuthError,
    LLMProvider,
    NetworkError,
    ProviderError,
    RateLimitError,
    SchemaValidationError,
    SearchProvider,
    SearchResult,
)

T = TypeVar("T", bound=BaseModel)


class FakeLLMProvider:
    """Deterministic LLM test double for offline testing."""
    
    def __init__(
        self,
        default_text: str = "This is a deterministic fake response.",
        structured_responses: Optional[Dict[str, Any]] = None,
        simulate_error: Optional[Exception] = None,
    ):
        self.default_text = default_text
        self.structured_responses: Dict[str, Any] = structured_responses or {}
        self.simulate_error = simulate_error
        self.call_history: List[Dict[str, Any]] = []

    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        self.call_history.append({"prompt": prompt, "system_instruction": system_instruction, "type": "text"})
        if self.simulate_error:
            raise self.simulate_error
        return self.default_text

    def generate_structured(
        self,
        prompt: str,
        schema_class: Type[T],
        system_instruction: Optional[str] = None,
    ) -> T:
        self.call_history.append({
            "prompt": prompt,
            "system_instruction": system_instruction,
            "schema_class": schema_class.__name__,
            "type": "structured"
        })
        if self.simulate_error:
            raise self.simulate_error

        # Check if an explicit response object or dict was provided for this schema name
        schema_name = schema_class.__name__
        if schema_name in self.structured_responses:
            data = self.structured_responses[schema_name]
            if isinstance(data, schema_class):
                return data
            if isinstance(data, dict):
                return schema_class.model_validate(data)
            if isinstance(data, str):
                try:
                    parsed = json.loads(data)
                    return schema_class.model_validate(parsed)
                except Exception as exc:
                    raise SchemaValidationError(f"Could not parse test double json: {exc}", "fake_llm")

        # Fallback to model_validate with dummy required data or construct default
        try:
            # Try construct minimal dummy instance
            dummy_data = self._generate_minimal_dummy(schema_class)
            return schema_class.model_validate(dummy_data)
        except Exception as e:
            raise SchemaValidationError(f"FakeLLM could not auto-generate {schema_name}: {e}", "fake_llm")

    def _generate_minimal_dummy(self, schema_class: Type[BaseModel]) -> Dict[str, Any]:
        """Produce minimal valid data for known schema classes."""
        name = schema_class.__name__
        if name == "ResearchPlan":
            return {
                "question": "Sample Question",
                "rationale": "Deterministic fake rationale",
                "steps": [
                    {
                        "step_number": 1,
                        "tool": "web_search",
                        "goal": "Search sample info",
                        "action_input": "sample test query",
                        "status": "pending",
                    }
                ],
                "estimated_search_queries": 1,
                "estimated_target_urls": 1,
            }
        if name == "StructuredAnswer":
            return {
                "question": "Sample Question",
                "short_answer": "This is a deterministic fake short answer.",
                "key_findings": [
                    {
                        "statement": "Key finding supported by evidence.",
                        "source_ids": ["S1"],
                        "confidence": 0.9,
                    }
                ],
                "sources": [
                    {
                        "id": "S1",
                        "url": "https://example.com/info",
                        "title": "Example Source",
                        "snippet": "Example snippet content",
                        "quality_score": 0.9,
                    }
                ],
                "confidence_score": 0.85,
                "confidence_rationale": "High quality verifiable test data.",
                "assumptions": ["Assumed test environment."],
                "limitations": ["Mock data only."],
                "next_steps": ["Verify with live source."],
            }
        return {}


class FakeSearchProvider:
    """Deterministic web search test double for offline testing."""
    
    def __init__(
        self,
        default_results: Optional[List[SearchResult]] = None,
        query_responses: Optional[Dict[str, List[SearchResult]]] = None,
        simulate_error: Optional[Exception] = None,
    ):
        self.default_results: List[SearchResult] = default_results or [
            SearchResult(
                url="https://en.wikipedia.org/wiki/Artificial_intelligence",
                title="Artificial intelligence - Wikipedia",
                snippet="Artificial intelligence is the intelligence of machines or software.",
                score=0.95,
            ),
            SearchResult(
                url="https://arxiv.org/abs/2301.00001",
                title="Recent Advances in AI Research",
                snippet="We present a comprehensive overview of recent advances in AI systems.",
                score=0.88,
            ),
        ]
        self.query_responses: Dict[str, List[SearchResult]] = query_responses or {}
        self.simulate_error = simulate_error
        self.queries_executed: List[str] = []

    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        self.queries_executed.append(query)
        if self.simulate_error:
            raise self.simulate_error
        
        results = self.query_responses.get(query.strip().lower(), self.default_results)
        return results[:max_results]
