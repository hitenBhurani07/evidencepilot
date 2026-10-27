"""Unit tests for grounded synthesis, citation validation, and markdown formatting."""

import pytest
from evidencepilot.agent.synthesizer import (
    ResearchSynthesizer,
    SynthesisPayload,
    format_answer_markdown,
)
from evidencepilot.providers.base import ProviderError
from evidencepilot.providers.fakes import FakeLLMProvider
from evidencepilot.schemas.research import (
    Finding,
    ResearchRequest,
    RunMetadata,
    SourceItem,
    StructuredAnswer,
)


@pytest.fixture
def sample_sources():
    return [
        SourceItem(
            id="S1",
            url="https://cisa.gov/ai-guidance",
            title="CISA Secure AI Deployment",
            snippet="Federal guidelines recommend continuous adversarial testing.",
            full_content="Full detailed technical guide on securing enterprise AI models...",
            domain="cisa.gov",
            quality_score=0.95,
        ),
        SourceItem(
            id="S2",
            url="https://arxiv.org/abs/2301.00001",
            title="Prompt Injection Vulnerabilities in LLMs",
            snippet="Direct and indirect prompt injections represent critical risks.",
            domain="arxiv.org",
            quality_score=0.90,
        ),
    ]


@pytest.fixture
def sample_metadata():
    return RunMetadata(
        model_name="test-model",
        search_provider="TestSearch",
        tool_calls_count={"web_search": 1, "fetch_page": 1, "quality_filter": 1},
        is_mock_run=True,
    )


def test_synthesis_happy_path(sample_sources, sample_metadata):
    fake_payload = SynthesisPayload(
        short_answer="AI systems face prompt injection and data poisoning vulnerabilities.",
        key_findings=[
            Finding(
                statement="Adversarial prompt injection allows attackers to manipulate model outputs.",
                source_ids=["S1", "S2"],
                confidence=0.92,
            )
        ],
        confidence_score=0.88,
        confidence_rationale="Authoritative research papers and federal cybersecurity consensus.",
        assumptions=["Standard transformer architecture assumptions."],
        limitations=["Evolving threat landscape."],
        next_steps=["Deploy input sanitization defenses."],
    )

    fake_llm = FakeLLMProvider(
        structured_responses={"SynthesisPayload": fake_payload}
    )

    synthesizer = ResearchSynthesizer(llm_provider=fake_llm)
    req = ResearchRequest(query="What are the top AI security threats?")
    answer = synthesizer.synthesize(req, sample_sources, sample_metadata)

    assert isinstance(answer, StructuredAnswer)
    assert answer.question == req.query
    assert answer.short_answer == fake_payload.short_answer
    assert len(answer.key_findings) == 1
    assert answer.key_findings[0].source_ids == ["S1", "S2"]
    assert len(answer.sources) == 2
    assert answer.confidence_score == 0.88


def test_synthesis_filters_unknown_source_ids(sample_sources, sample_metadata):
    """Hallucinated source IDs not present in current run must be removed."""
    fake_payload = SynthesisPayload(
        short_answer="Test answer statement.",
        key_findings=[
            Finding(
                statement="Statement citing valid S1 and fake S99/S999.",
                source_ids=["S1", "S99", "S999"],
                confidence=0.85,
            )
        ],
        confidence_score=0.8,
        confidence_rationale="Test rationale.",
    )

    fake_llm = FakeLLMProvider(
        structured_responses={"SynthesisPayload": fake_payload}
    )

    synthesizer = ResearchSynthesizer(llm_provider=fake_llm)
    req = ResearchRequest(query="Test query")
    answer = synthesizer.synthesize(req, sample_sources, sample_metadata)

    # S99 and S999 must be stripped, leaving only S1
    assert answer.key_findings[0].source_ids == ["S1"]


def test_synthesis_penalizes_completely_ungrounded_finding(sample_sources, sample_metadata):
    """When a finding cites ONLY hallucinated IDs, confidence is penalized."""
    fake_payload = SynthesisPayload(
        short_answer="Test answer statement.",
        key_findings=[
            Finding(
                statement="Ungrounded statement.",
                source_ids=["S_HALLUCINATED"],
                confidence=0.90,
            )
        ],
        confidence_score=0.7,
        confidence_rationale="Test rationale.",
    )

    fake_llm = FakeLLMProvider(
        structured_responses={"SynthesisPayload": fake_payload}
    )

    synthesizer = ResearchSynthesizer(llm_provider=fake_llm)
    req = ResearchRequest(query="Test query")
    answer = synthesizer.synthesize(req, sample_sources, sample_metadata)

    # Source IDs empty, confidence halved
    assert answer.key_findings[0].source_ids == []
    assert answer.key_findings[0].confidence <= 0.45


def test_synthesis_fallback_on_llm_error(sample_sources, sample_metadata):
    """If LLM synthesis fails with network/rate-limit error, fallback synthesis is generated."""
    failing_llm = FakeLLMProvider(simulate_error=ProviderError("Connection reset", "fake_llm"))
    synthesizer = ResearchSynthesizer(llm_provider=failing_llm)

    req = ResearchRequest(query="Test query with LLM error")
    answer = synthesizer.synthesize(req, sample_sources, sample_metadata)

    assert isinstance(answer, StructuredAnswer)
    assert "Synthesized research summary" in answer.short_answer
    assert "Deterministic fallback synthesis" in answer.confidence_rationale
    assert len(answer.key_findings) >= 1
    assert answer.key_findings[0].source_ids[0] in ["S1", "S2"]


def test_format_answer_markdown(sample_sources, sample_metadata):
    answer = StructuredAnswer(
        question="How do vector databases work?",
        short_answer="Vector databases index embeddings for high-dimensional approximate nearest neighbor search.",
        key_findings=[
            Finding(
                statement="HNSW and IVF-PQ algorithms optimize the recall-latency tradeoff.",
                source_ids=["S1"],
                confidence=0.95,
            )
        ],
        sources=sample_sources,
        confidence_score=0.91,
        confidence_rationale="Peer-reviewed algorithmic benchmarks and documentation.",
        assumptions=["Embeddings generated by compatible encoder."],
        limitations=["Recall drops under massive distributed shards."],
        next_steps=["Benchmark query throughput under production SLA."],
        metadata=sample_metadata,
    )

    md = format_answer_markdown(answer)
    assert "# Research Report: How do vector databases work?" in md
    assert "## Executive Summary" in md
    assert "## Key Findings" in md
    assert "HNSW and IVF-PQ algorithms optimize the recall-latency tradeoff." in md
    assert "`[S1]`" in md
    assert "## Verified Sources" in md
    assert "| **S1** |" in md
    assert "https://cisa.gov/ai-guidance" in md
    assert "## Run Metadata" in md
    assert "Execution Latency" in md
