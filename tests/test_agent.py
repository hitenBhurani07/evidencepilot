"""Unit and integration tests for ResearchPlanner, ResearchOrchestrator, and event bus."""

from unittest.mock import MagicMock, patch
import pytest

from evidencepilot.agent.events import EventBus, WorkflowEventType
from evidencepilot.agent.orchestrator import ResearchOrchestrator
from evidencepilot.agent.planner import ResearchPlanner
from evidencepilot.providers.base import ProviderError, SearchResult
from evidencepilot.providers.fakes import FakeLLMProvider, FakeSearchProvider
from evidencepilot.schemas.research import (
    Finding,
    PlanStep,
    ResearchPlan,
    ResearchRequest,
    StepStatus,
    StructuredAnswer,
    ToolType,
)
from evidencepilot.tools.extractor import ExtractionResult, PageExtractor


# ---------------------------------------------------------------------------
# Planner Tests
# ---------------------------------------------------------------------------

def test_planner_creates_bounded_plan():
    fake_llm = FakeLLMProvider()
    planner = ResearchPlanner(llm_provider=fake_llm, max_steps=3)
    
    req = ResearchRequest(query="Compare vector databases for edge deployment")
    plan = planner.create_plan(req)
    
    assert isinstance(plan, ResearchPlan)
    assert len(plan.steps) <= 3
    assert plan.steps[0].step_number == 1
    assert plan.steps[0].tool == ToolType.WEB_SEARCH


def test_planner_fallback_on_llm_failure():
    # Simulate LLM failure
    failing_llm = FakeLLMProvider(simulate_error=ProviderError("Rate limit exceeded", "fake_llm"))
    planner = ResearchPlanner(llm_provider=failing_llm)
    
    req = ResearchRequest(query="Quantum computing encryption risks")
    plan = planner.create_plan(req)
    
    assert isinstance(plan, ResearchPlan)
    assert "Fallback" in plan.rationale
    assert len(plan.steps) == 3
    assert plan.steps[0].tool == ToolType.WEB_SEARCH
    assert plan.steps[1].tool == ToolType.FETCH_PAGE


# ---------------------------------------------------------------------------
# Orchestrator Integration Tests
# ---------------------------------------------------------------------------

@patch.object(PageExtractor, "extract")
def test_orchestrator_happy_path(mock_extract):
    mock_extract.return_value = ExtractionResult(
        url="https://cisa.gov/ai-security",
        status_code=200,
        title="CISA AI Guidelines",
        content="Detailed cybersecurity guidelines for enterprise AI deployments...",
        is_success=True,
        byte_count=1024,
    )

    fake_search = FakeSearchProvider(
        default_results=[
            SearchResult(
                url="https://cisa.gov/ai-security",
                title="CISA AI Guidelines",
                snippet="Cybersecurity guidelines for AI.",
                score=0.95,
            ),
            SearchResult(
                url="https://arxiv.org/abs/2301.00001",
                title="AI Threat Models",
                snippet="Comprehensive analysis of generative AI threat models.",
                score=0.90,
            ),
        ]
    )
    fake_llm = FakeLLMProvider()
    events_recorded = []
    bus = EventBus(listener=lambda ev: events_recorded.append(ev.event_type))

    orchestrator = ResearchOrchestrator(
        llm_provider=fake_llm,
        search_provider=fake_search,
        event_bus=bus,
    )

    req = ResearchRequest(query="What are the top AI security threats?")
    answer = orchestrator.execute(req)

    assert isinstance(answer, StructuredAnswer)
    assert answer.question == req.query
    assert answer.confidence_score > 0.0
    assert len(answer.sources) >= 1
    assert len(answer.key_findings) >= 1
    assert answer.metadata.is_mock_run is True
    assert answer.metadata.total_latency_seconds is not None

    # Verify event sequence
    assert WorkflowEventType.REQUEST_VALIDATED in events_recorded
    assert WorkflowEventType.PLAN_CREATED in events_recorded
    assert WorkflowEventType.TOOL_CALLED in events_recorded
    assert WorkflowEventType.RUN_COMPLETED in events_recorded


@patch.object(PageExtractor, "extract")
def test_orchestrator_partial_tool_failure(mock_extract):
    """When 1 of 2 URLs fails extraction, orchestrator succeeds with partial results."""
    def side_effect(url):
        if "failing-site" in url:
            return ExtractionResult(
                url=url,
                is_success=False,
                error_message="HTTP server error 500",
            )
        return ExtractionResult(
            url=url,
            is_success=True,
            title="Success Site",
            content="Substantive valid research content that succeeds...",
            status_code=200,
        )

    mock_extract.side_effect = side_effect

    fake_search = FakeSearchProvider(
        default_results=[
            SearchResult(
                url="https://failing-site.com/error",
                title="Failing Site",
                snippet="Snippet from failing site.",
                score=0.5,
            ),
            SearchResult(
                url="https://working-site.org/good",
                title="Working Site",
                snippet="Snippet from working site with valid text.",
                score=0.88,
            ),
        ]
    )
    orchestrator = ResearchOrchestrator(
        llm_provider=FakeLLMProvider(),
        search_provider=fake_search,
    )

    req = ResearchRequest(query="Partial failure test query")
    answer = orchestrator.execute(req)

    assert isinstance(answer, StructuredAnswer)
    assert answer.confidence_score > 0.0
    # At least the working site should be present
    assert any("working-site" in s.url for s in answer.sources)


def test_orchestrator_total_tools_failure():
    """When search fails and returns 0 sources, orchestrator produces structured zero-evidence refusal."""
    empty_search = FakeSearchProvider(default_results=[])
    orchestrator = ResearchOrchestrator(
        llm_provider=FakeLLMProvider(),
        search_provider=empty_search,
    )

    req = ResearchRequest(query="Unreachable query with zero results")
    answer = orchestrator.execute(req)

    assert isinstance(answer, StructuredAnswer)
    assert answer.confidence_score == 0.0
    assert "No verifiable evidence could be gathered" in answer.short_answer
    assert len(answer.sources) == 0
    assert len(answer.key_findings) == 1
    assert answer.key_findings[0].confidence == 0.0
    assert len(answer.next_steps) >= 1


def test_orchestrator_budget_caps():
    fake_search = FakeSearchProvider(
        default_results=[
            SearchResult(url=f"https://site{i}.org", title=f"Site {i}", snippet=f"Snippet {i} text for research.")
            for i in range(10)
        ]
    )
    orchestrator = ResearchOrchestrator(
        llm_provider=FakeLLMProvider(),
        search_provider=fake_search,
    )

    # Strictly limit budget
    req = ResearchRequest(
        query="Budget bounds test",
        max_search_queries=1,
        max_pages_to_fetch=2,
    )
    answer = orchestrator.execute(req)

    assert answer.metadata.tool_calls_count["web_search"] <= 1
    assert answer.metadata.tool_calls_count["fetch_page"] <= 2
