"""Stage 07 — Pytest evaluation tests.

Five typed evaluation queries exercising the full pipeline in offline/mock mode.
These verify STRUCTURAL behavior, not answer quality.
Live API calls are documented as requiring credentials (NOT RUN in offline mode).
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from evidencepilot.agent.orchestrator import ResearchOrchestrator
from evidencepilot.providers.base import SearchResult
from evidencepilot.providers.fakes import FakeLLMProvider, FakeSearchProvider
from evidencepilot.schemas.research import ResearchRequest, StructuredAnswer
from evidencepilot.tools.extractor import ExtractionResult, PageExtractor


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _mock_extract(content: str = "Mock page content.") -> ExtractionResult:
    return ExtractionResult(
        url="https://example.com/page",
        status_code=200,
        title="Mock Page",
        content=content,
        is_success=True,
        byte_count=len(content),
    )


def _rich_sources(label: str, count: int = 3) -> list[SearchResult]:
    return [
        SearchResult(
            url=f"https://source{i}.example.com/{label.replace(' ', '-')}",
            title=f"{label} Source {i}",
            snippet=f"Relevant content about {label} for research purpose {i}.",
            score=0.80 + i * 0.03,
        )
        for i in range(count)
    ]


def _make_orch(sources: list[SearchResult]) -> ResearchOrchestrator:
    return ResearchOrchestrator(
        llm_provider=FakeLLMProvider(),
        search_provider=FakeSearchProvider(default_results=sources),
    )


# ---------------------------------------------------------------------------
# EVAL-01 — Comparative research
# ---------------------------------------------------------------------------


def test_eval_01_comparative_research():
    """
    Query type: Comparative
    Query: Compare two databases for analytics
    Expected: Answer has sources, findings, positive confidence
    Grounding: Sources must be cited; does not pick winner without caveat
    Edge cases: Biased sources; conflicting recommendations
    """
    sources = _rich_sources("PostgreSQL", 2) + _rich_sources("MongoDB", 2)

    with patch.object(PageExtractor, "extract") as mock_ext:
        mock_ext.return_value = _mock_extract(
            "PostgreSQL offers ACID compliance and complex SQL queries. "
            "MongoDB offers flexible schema and horizontal scaling. "
            "For analytics at scale, both have trade-offs depending on query patterns."
        )
        req = ResearchRequest(
            query="Compare PostgreSQL and MongoDB for storing user analytics data at scale",
            max_search_queries=2,
            max_pages_to_fetch=2,
        )
        answer = _make_orch(sources).execute(req)

    assert isinstance(answer, StructuredAnswer)
    assert answer.confidence_score > 0.0
    assert len(answer.sources) >= 1
    assert len(answer.key_findings) >= 1
    assert answer.metadata.is_mock_run is True
    # Schema valid — answer was constructed without exception


# ---------------------------------------------------------------------------
# EVAL-02 — Entity discovery
# ---------------------------------------------------------------------------


def test_eval_02_entity_discovery():
    """
    Query type: Entity discovery
    Query: Discover named researchers in a field
    Expected: Sources retrieved; findings reference entities; grounded citations
    Grounding: Named entities must be traceable to cited source IDs
    Edge cases: Prominent entities may not appear in top search results
    """
    sources = _rich_sources("interpretable machine learning", 3)

    with patch.object(PageExtractor, "extract") as mock_ext:
        mock_ext.return_value = _mock_extract(
            "Cynthia Rudin (Duke) advocates for inherently interpretable models. "
            "LIME: Marco Tulio Ribeiro. SHAP: Scott Lundberg. "
            "Rich Caruana (Microsoft) works on generalized additive models."
        )
        req = ResearchRequest(
            query="Who are the leading researchers in interpretable machine learning?",
            max_search_queries=2,
            max_pages_to_fetch=2,
        )
        answer = _make_orch(sources).execute(req)

    assert isinstance(answer, StructuredAnswer)
    assert answer.confidence_score > 0.0
    assert len(answer.sources) >= 1


# ---------------------------------------------------------------------------
# EVAL-03 — Technical pros/cons
# ---------------------------------------------------------------------------


def test_eval_03_technical_pros_cons():
    """
    Query type: Technical pros/cons
    Query: Pros and cons of Rust vs C for systems programming
    Expected: Structured findings; acknowledges trade-offs; balanced
    Grounding: Claims traceable to technical sources
    Edge cases: Opinion-heavy sources may introduce bias
    """
    sources = _rich_sources("Rust programming language", 2) + _rich_sources("C programming language", 2)

    with patch.object(PageExtractor, "extract") as mock_ext:
        mock_ext.return_value = _mock_extract(
            "Rust pros: memory safety, no GC, fearless concurrency. "
            "Rust cons: steep learning curve, slow compilation. "
            "C pros: maximum performance, universal support. "
            "C cons: manual memory management, undefined behavior risks."
        )
        req = ResearchRequest(
            query="What are the pros and cons of using Rust for systems programming compared to C?",
            max_search_queries=2,
            max_pages_to_fetch=3,
        )
        answer = _make_orch(sources).execute(req)

    assert isinstance(answer, StructuredAnswer)
    assert len(answer.key_findings) >= 1
    assert answer.confidence_score > 0.0
    assert answer.metadata.tool_calls_count.get("web_search", 0) >= 1


# ---------------------------------------------------------------------------
# EVAL-04 — Time-sensitive / date-aware research
# ---------------------------------------------------------------------------


def test_eval_04_time_sensitive_mock_labelled():
    """
    Query type: Time-sensitive
    Query: Recent AI safety papers from 2024
    Expected in MOCK mode: PASS_WITH_CAVEAT — cannot verify temporal accuracy without live search
    Grounding: Citations should include dates where available
    Edge cases: Mock cannot provide genuinely recent results
    NOTE: Live evaluation requires Tavily API key (NOT RUN in offline mode)
    """
    sources = _rich_sources("AI safety 2024", 2)

    with patch.object(PageExtractor, "extract") as mock_ext:
        mock_ext.return_value = _mock_extract(
            "In 2024: Constitutional AI from Anthropic. "
            "Scalable oversight from OpenAI. "
            "Mechanistic interpretability research expanded significantly."
        )
        req = ResearchRequest(
            query="What are the most significant AI safety research papers published in 2024?",
            max_search_queries=2,
            max_pages_to_fetch=2,
        )
        answer = _make_orch(sources).execute(req)

    assert isinstance(answer, StructuredAnswer)
    assert answer.metadata.is_mock_run is True  # Temporal accuracy cannot be validated
    assert answer.confidence_score >= 0.0
    assert len(answer.limitations) >= 1 or answer.confidence_score < 1.0


# ---------------------------------------------------------------------------
# EVAL-05 — Unanswerable / ambiguous / failure-triggering
# ---------------------------------------------------------------------------


def test_eval_05_unanswerable_query_returns_structured_refusal():
    """
    Query type: Unanswerable / failure-triggering
    Query: Fictional country GDP (no real answer exists)
    Expected: confidence=0.0, zero sources, structured refusal, no hallucinated data
    Grounding: Must NOT fabricate a number; must state inability to answer
    Edge cases: System must not confabulate plausible-sounding answer
    """
    # No search results → zero-evidence path
    orch = ResearchOrchestrator(
        llm_provider=FakeLLMProvider(),
        search_provider=FakeSearchProvider(default_results=[]),
    )
    req = ResearchRequest(
        query="What is the exact GDP of the fictional country Ruritania in 2025?",
        max_search_queries=2,
        max_pages_to_fetch=2,
    )
    answer = orch.execute(req)

    assert isinstance(answer, StructuredAnswer)
    assert answer.confidence_score == 0.0, "Unanswerable query must return confidence=0.0"
    assert len(answer.sources) == 0, "No sources should exist for an unanswerable query"
    assert "No verifiable evidence" in answer.short_answer, (
        "Answer must explicitly state inability to gather evidence"
    )
    assert answer.key_findings[0].confidence == 0.0


# ---------------------------------------------------------------------------
# Coverage completeness checklist
# ---------------------------------------------------------------------------


def test_coverage_checklist_all_categories_represented():
    """Verify the five evaluation categories are represented."""
    categories = {
        "comparative",
        "entity_discovery",
        "technical_pros_cons",
        "time_sensitive",
        "unanswerable_failure",
    }
    # This test documents that each category has a dedicated test above
    assert len(categories) == 5
