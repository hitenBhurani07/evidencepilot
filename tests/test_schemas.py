"""Unit tests for Pydantic domain schemas."""

import pytest
from pydantic import ValidationError
from evidencepilot.schemas.research import (
    Finding,
    PlanStep,
    ResearchPlan,
    ResearchRequest,
    RunMetadata,
    SourceItem,
    StepStatus,
    StructuredAnswer,
    ToolType,
)


def test_research_request_validation():
    # Valid request
    req = ResearchRequest(query="What is the impact of LLMs on cybersecurity?")
    assert req.query == "What is the impact of LLMs on cybersecurity?"
    assert req.max_search_queries == 3
    assert req.max_pages_to_fetch == 4

    # Whitespace stripping
    req2 = ResearchRequest(query="   Trimmed question?   ")
    assert req2.query == "Trimmed question?"

    # Empty query rejected
    with pytest.raises(ValidationError):
        ResearchRequest(query="")

    with pytest.raises(ValidationError):
        ResearchRequest(query="   ")

    # Too short
    with pytest.raises(ValidationError):
        ResearchRequest(query="ab")


def test_research_plan_validation():
    step = PlanStep(
        step_number=1,
        tool=ToolType.WEB_SEARCH,
        goal="Find overview articles",
        action_input="AI cyber threats overview",
        status=StepStatus.PENDING,
    )
    plan = ResearchPlan(
        question="What are AI threats?",
        rationale="Step-by-step search and content analysis.",
        steps=[step],
        estimated_search_queries=1,
        estimated_target_urls=2,
    )
    assert len(plan.steps) == 1
    assert plan.steps[0].tool == ToolType.WEB_SEARCH

    # Invalid tool type rejected
    with pytest.raises(ValidationError):
        PlanStep(
            step_number=1,
            tool="nonexistent_tool",  # type: ignore
            goal="Goal",
            action_input="input",
        )


def test_source_item_validation():
    source = SourceItem(
        id="S1",
        url="https://cisa.gov/ai-guidelines",
        title="CISA AI Guidelines",
        snippet="Official federal guidelines on secure AI implementation.",
        quality_score=0.95,
    )
    assert source.id == "S1"
    assert source.quality_score == 0.95
    assert not source.is_filtered_out

    # Score out of bounds (must be 0.0 to 1.0)
    with pytest.raises(ValidationError):
        SourceItem(
            id="S2",
            url="https://example.com",
            title="Title",
            quality_score=1.5,
        )


def test_finding_validation():
    finding = Finding(
        statement="AI systems face novel prompt injection vulnerabilities.",
        source_ids=["S1", "S2"],
        confidence=0.9,
    )
    assert len(finding.source_ids) == 2
    assert finding.confidence == 0.9

    # Confidence out of bounds
    with pytest.raises(ValidationError):
        Finding(
            statement="Invalid confidence statement",
            source_ids=["S1"],
            confidence=1.2,
        )


def test_structured_answer_validation():
    answer = StructuredAnswer(
        question="What are the risks of prompt injection?",
        short_answer="Prompt injection allows untrusted inputs to manipulate agent control flow.",
        key_findings=[
            Finding(
                statement="Indirect prompt injection occurs via third-party web content.",
                source_ids=["S1"],
                confidence=0.85,
            )
        ],
        sources=[
            SourceItem(
                id="S1",
                url="https://owasp.org/llm-top-10",
                title="OWASP Top 10 for LLMs",
                snippet="Prompt injection ranks as the top vulnerability.",
                quality_score=0.95,
            )
        ],
        confidence_score=0.88,
        confidence_rationale="High quality authoritative security framework consensus.",
        assumptions=["Attacker supplies adversarial web pages."],
        limitations=["Evolving threat landscape."],
        next_steps=["Deploy input sanitization and delimiter tags."],
    )
    assert answer.confidence_score == 0.88
    assert len(answer.key_findings) == 1
    assert len(answer.sources) == 1
    assert answer.sources[0].id == "S1"

    # Missing mandatory field rejected
    with pytest.raises(ValidationError):
        StructuredAnswer(
            question="Incomplete answer",
            short_answer="Missing key findings",
            key_findings=[],  # min_length=1
            sources=[],
            confidence_score=0.5,
            confidence_rationale="Rationale",
        )
