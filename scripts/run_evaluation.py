"""Stage 07 — Evaluation suite with five typed query categories.

Runs the full pipeline in mock/offline mode and saves outputs to artifacts/.
Execute with:
    .venv\\Scripts\\python scripts/run_evaluation.py
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

# Allow running from project root
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from evidencepilot.agent.orchestrator import ResearchOrchestrator
from evidencepilot.providers.base import NetworkError, RateLimitError, SearchResult
from evidencepilot.providers.fakes import FakeLLMProvider, FakeSearchProvider
from evidencepilot.schemas.research import ResearchRequest
from evidencepilot.tools.extractor import ExtractionResult, PageExtractor

ARTIFACTS_DIR = Path(__file__).parent.parent / "artifacts"
ARTIFACTS_DIR.mkdir(exist_ok=True)

RUN_TIMESTAMP = datetime.now(timezone.utc).isoformat(timespec="seconds")
RUN_MODE = "MOCK_OFFLINE"


# ---------------------------------------------------------------------------
# Helper: build a standard orchestrator with fake providers
# ---------------------------------------------------------------------------

def _make_orchestrator(search_results: list[SearchResult] | None = None) -> ResearchOrchestrator:
    return ResearchOrchestrator(
        llm_provider=FakeLLMProvider(),
        search_provider=FakeSearchProvider(default_results=search_results),
    )


def _make_rich_sources(label: str) -> list[SearchResult]:
    """Return realistic-looking fake sources for a given topic label."""
    return [
        SearchResult(
            url=f"https://en.wikipedia.org/wiki/{label.replace(' ', '_')}",
            title=f"{label} — Wikipedia",
            snippet=f"Comprehensive overview of {label} covering history, mechanisms, and applications.",
            score=0.93,
        ),
        SearchResult(
            url=f"https://arxiv.org/abs/2310.{hash(label) % 99999:05d}",
            title=f"Recent Advances in {label} (2024)",
            snippet=f"This paper surveys {label} from a computational perspective, examining state-of-the-art methods.",
            score=0.88,
        ),
        SearchResult(
            url=f"https://www.nature.com/articles/{hash(label) % 99999:08d}",
            title=f"Nature: {label} — Review Article",
            snippet=f"Peer-reviewed review of {label} published in Nature, covering clinical and research aspects.",
            score=0.96,
        ),
    ]


# ---------------------------------------------------------------------------
# EVALUATION QUERY 1 — Comparative research
# ---------------------------------------------------------------------------

def eval_01_comparative():
    """Compare two competing technologies or approaches."""
    query = "Compare PostgreSQL and MongoDB for storing user analytics data at scale"

    sources = _make_rich_sources("PostgreSQL") + _make_rich_sources("MongoDB")
    orch = _make_orchestrator(sources)

    with patch.object(PageExtractor, "extract") as mock_extract:
        mock_extract.return_value = ExtractionResult(
            url="https://en.wikipedia.org/wiki/PostgreSQL",
            status_code=200,
            title="PostgreSQL — Wikipedia",
            content=(
                "PostgreSQL is a powerful open-source relational database with ACID compliance. "
                "MongoDB is a document database with horizontal scalability. "
                "For analytics at scale, PostgreSQL offers better SQL support and joins, "
                "while MongoDB offers flexible schemas and horizontal sharding."
            ),
            is_success=True,
            byte_count=2048,
        )
        req = ResearchRequest(query=query, max_search_queries=2, max_pages_to_fetch=2)
        answer = orch.execute(req)

    return {
        "eval_id": "EVAL-01",
        "type": "comparative",
        "query": query,
        "expected_tools": ["web_search", "fetch_page", "quality_filter"],
        "expected_behavior": "Answer compares both options with evidence; does not pick a winner without caveat",
        "grounding_requirement": "Must cite sources; confidence score reflects uncertainty",
        "edge_cases": ["One source may be biased towards one option"],
        "run_mode": RUN_MODE,
        "run_timestamp": RUN_TIMESTAMP,
        "outcome": {
            "status": "PASS" if answer.confidence_score > 0 and len(answer.sources) >= 1 else "FAIL",
            "confidence_score": answer.confidence_score,
            "sources_used": len(answer.sources),
            "short_answer_preview": answer.short_answer[:200],
            "findings_count": len(answer.key_findings),
            "is_mock_run": answer.metadata.is_mock_run,
        },
        "defects": [],
        "fix_status": "N/A",
    }


# ---------------------------------------------------------------------------
# EVALUATION QUERY 2 — Entity discovery
# ---------------------------------------------------------------------------

def eval_02_entity_discovery():
    """Discover entities (companies, researchers, products) related to a topic."""
    query = "Who are the leading researchers in interpretable machine learning?"

    sources = _make_rich_sources("Interpretable machine learning") + _make_rich_sources("LIME SHAP Explainability")
    orch = _make_orchestrator(sources)

    with patch.object(PageExtractor, "extract") as mock_extract:
        mock_extract.return_value = ExtractionResult(
            url="https://arxiv.org/abs/2310.00001",
            status_code=200,
            title="Interpretable ML Researchers",
            content=(
                "Notable researchers in interpretable machine learning include Cynthia Rudin at Duke University, "
                "who advocates for inherently interpretable models. LIME was developed by Marco Tulio Ribeiro. "
                "SHAP was introduced by Scott Lundberg. Rich Caruana at Microsoft has worked on GAMs."
            ),
            is_success=True,
            byte_count=1500,
        )
        req = ResearchRequest(query=query, max_search_queries=2, max_pages_to_fetch=2)
        answer = orch.execute(req)

    return {
        "eval_id": "EVAL-02",
        "type": "entity_discovery",
        "query": query,
        "expected_tools": ["web_search", "fetch_page", "quality_filter"],
        "expected_behavior": "Lists specific named researchers with institution affiliations and notable contributions",
        "grounding_requirement": "Entity names must be traceable to cited sources",
        "edge_cases": ["Some prominent researchers may not appear in top search results"],
        "run_mode": RUN_MODE,
        "run_timestamp": RUN_TIMESTAMP,
        "outcome": {
            "status": "PASS" if answer.confidence_score > 0 and len(answer.sources) >= 1 else "FAIL",
            "confidence_score": answer.confidence_score,
            "sources_used": len(answer.sources),
            "short_answer_preview": answer.short_answer[:200],
            "findings_count": len(answer.key_findings),
            "is_mock_run": answer.metadata.is_mock_run,
        },
        "defects": [],
        "fix_status": "N/A",
    }


# ---------------------------------------------------------------------------
# EVALUATION QUERY 3 — Technical pros/cons
# ---------------------------------------------------------------------------

def eval_03_technical_pros_cons():
    """List pros and cons for a technical decision."""
    query = "What are the pros and cons of using Rust for systems programming compared to C?"

    sources = _make_rich_sources("Rust programming language") + _make_rich_sources("C programming language")
    orch = _make_orchestrator(sources)

    with patch.object(PageExtractor, "extract") as mock_extract:
        mock_extract.return_value = ExtractionResult(
            url="https://en.wikipedia.org/wiki/Rust_(programming_language)",
            status_code=200,
            title="Rust programming language",
            content=(
                "Rust pros: memory safety without garbage collection, zero-cost abstractions, fearless concurrency. "
                "Rust cons: steep learning curve, slower compilation, smaller ecosystem than C. "
                "C pros: maximum performance, universal compiler support, decades of libraries. "
                "C cons: manual memory management, undefined behavior risks, no built-in safety guarantees."
            ),
            is_success=True,
            byte_count=2200,
        )
        req = ResearchRequest(query=query, max_search_queries=2, max_pages_to_fetch=3)
        answer = orch.execute(req)

    return {
        "eval_id": "EVAL-03",
        "type": "technical_pros_cons",
        "query": query,
        "expected_tools": ["web_search", "fetch_page", "quality_filter"],
        "expected_behavior": "Structured pro/con list; honest about trade-offs; does not declare a definitive winner",
        "grounding_requirement": "Pros and cons traceable to cited technical sources",
        "edge_cases": ["Opinion-heavy sources may introduce bias"],
        "run_mode": RUN_MODE,
        "run_timestamp": RUN_TIMESTAMP,
        "outcome": {
            "status": "PASS" if answer.confidence_score > 0 and len(answer.key_findings) >= 1 else "FAIL",
            "confidence_score": answer.confidence_score,
            "sources_used": len(answer.sources),
            "short_answer_preview": answer.short_answer[:200],
            "findings_count": len(answer.key_findings),
            "is_mock_run": answer.metadata.is_mock_run,
        },
        "defects": [],
        "fix_status": "N/A",
    }


# ---------------------------------------------------------------------------
# EVALUATION QUERY 4 — Time-sensitive / date-aware research
# ---------------------------------------------------------------------------

def eval_04_time_sensitive():
    """Time-sensitive research where recency matters."""
    query = "What are the most significant AI safety research papers published in 2024?"

    sources = _make_rich_sources("AI safety 2024") + _make_rich_sources("Large language model alignment 2024")
    orch = _make_orchestrator(sources)

    with patch.object(PageExtractor, "extract") as mock_extract:
        mock_extract.return_value = ExtractionResult(
            url="https://arxiv.org/abs/2401.00001",
            status_code=200,
            title="AI Safety 2024 Review",
            content=(
                "In 2024, major AI safety papers include work on constitutional AI from Anthropic, "
                "scalable oversight experiments from OpenAI, and mechanistic interpretability research. "
                "Note: this mock content represents simulated data; live search would provide current papers."
            ),
            is_success=True,
            byte_count=1800,
        )
        req = ResearchRequest(query=query, max_search_queries=2, max_pages_to_fetch=2)
        answer = orch.execute(req)

    return {
        "eval_id": "EVAL-04",
        "type": "time_sensitive",
        "query": query,
        "expected_tools": ["web_search", "fetch_page", "quality_filter"],
        "expected_behavior": "Should note recency limitation; flag that mocked data may not reflect real 2024 publications",
        "grounding_requirement": "Citations should include publication dates where available",
        "edge_cases": [
            "Mock mode cannot provide genuinely recent results",
            "Live run should show papers from after training cutoff",
        ],
        "run_mode": RUN_MODE,
        "run_timestamp": RUN_TIMESTAMP,
        "outcome": {
            "status": "PASS_WITH_CAVEAT" if answer.metadata.is_mock_run else (
                "PASS" if answer.confidence_score > 0 else "FAIL"
            ),
            "confidence_score": answer.confidence_score,
            "sources_used": len(answer.sources),
            "short_answer_preview": answer.short_answer[:200],
            "findings_count": len(answer.key_findings),
            "is_mock_run": answer.metadata.is_mock_run,
            "caveat": "Mock run: temporal accuracy cannot be validated without live search",
        },
        "defects": ["Mock mode cannot verify recency; live evaluation needed with Tavily credentials"],
        "fix_status": "Pending live API credentials",
    }


# ---------------------------------------------------------------------------
# EVALUATION QUERY 5 — Unanswerable / ambiguous / failure-triggering
# ---------------------------------------------------------------------------

def eval_05_unanswerable():
    """Query that should result in zero evidence or explicit uncertainty."""
    query = "What is the exact GDP of the fictional country Ruritania in 2025?"

    orch = _make_orchestrator(search_results=[])  # Explicitly no results
    req = ResearchRequest(query=query, max_search_queries=2, max_pages_to_fetch=2)
    answer = orch.execute(req)

    return {
        "eval_id": "EVAL-05",
        "type": "unanswerable_failure",
        "query": query,
        "expected_tools": ["web_search"],
        "expected_behavior": "System returns confidence=0, refuses to fabricate, states no evidence found",
        "grounding_requirement": "Must NOT hallucinate a GDP figure; must state inability to answer",
        "edge_cases": ["System must not confabulate a plausible-sounding number"],
        "run_mode": RUN_MODE,
        "run_timestamp": RUN_TIMESTAMP,
        "outcome": {
            "status": "PASS" if answer.confidence_score == 0.0 and len(answer.sources) == 0 else "FAIL",
            "confidence_score": answer.confidence_score,
            "sources_used": len(answer.sources),
            "short_answer_preview": answer.short_answer[:200],
            "findings_count": len(answer.key_findings),
            "is_mock_run": answer.metadata.is_mock_run,
        },
        "defects": [],
        "fix_status": "N/A",
    }


# ---------------------------------------------------------------------------
# Evaluation rubric
# ---------------------------------------------------------------------------

RUBRIC = {
    "rubric_version": "1.0",
    "note": (
        "This rubric is illustrative for a small evaluation set. "
        "It is NOT a scientific benchmark. Results in mock mode validate "
        "structural behavior, not answer quality."
    ),
    "dimensions": [
        {
            "name": "evidence_relevance",
            "description": "Cited sources are topically relevant to the query",
            "max_score": 5,
        },
        {
            "name": "citation_traceability",
            "description": "Every finding cites at least one source ID that exists in answer.sources",
            "max_score": 5,
        },
        {
            "name": "answer_coverage",
            "description": "Short answer addresses the main intent of the query",
            "max_score": 5,
        },
        {
            "name": "uncertainty_honesty",
            "description": "Confidence score and rationale honestly reflect evidence completeness",
            "max_score": 5,
        },
        {
            "name": "failure_robustness",
            "description": "Zero-evidence case returns structured refusal, not fabrication",
            "max_score": 5,
        },
        {
            "name": "output_schema_validity",
            "description": "StructuredAnswer passes Pydantic validation without errors",
            "max_score": 5,
        },
    ],
    "scoring_note": "Scores are assigned only to evidence actually observed in test runs, not theoretical capability.",
}


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("EvidencePilot — Stage 07 Evaluation Suite")
    print(f"Mode: {RUN_MODE}  |  Timestamp: {RUN_TIMESTAMP}")
    print("=" * 60)

    results = []
    for fn, label in [
        (eval_01_comparative,      "EVAL-01 Comparative"),
        (eval_02_entity_discovery, "EVAL-02 Entity Discovery"),
        (eval_03_technical_pros_cons, "EVAL-03 Pros/Cons"),
        (eval_04_time_sensitive,   "EVAL-04 Time-Sensitive"),
        (eval_05_unanswerable,     "EVAL-05 Unanswerable"),
    ]:
        print(f"\nRunning {label}...", end=" ", flush=True)
        try:
            result = fn()
            status = result["outcome"]["status"]
            print(f"[{status}]")
            results.append(result)
        except Exception as exc:
            print(f"[ERROR: {exc}]")
            results.append({"eval_id": label, "outcome": {"status": "ERROR"}, "error": str(exc)})

    # Save individual sample outputs
    for r in results:
        eval_id = r.get("eval_id", "unknown")
        out_path = ARTIFACTS_DIR / f"{eval_id.lower().replace('-', '_')}_mock_output.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(r, f, indent=2, default=str)
        print(f"  Saved: {out_path}")

    # Save combined report
    report = {
        "report_version": "1.0",
        "run_mode": RUN_MODE,
        "run_timestamp": RUN_TIMESTAMP,
        "evaluations": results,
        "rubric": RUBRIC,
        "summary": {
            "total_queries": len(results),
            "pass_count": sum(1 for r in results if "PASS" in r.get("outcome", {}).get("status", "")),
            "fail_count": sum(1 for r in results if r.get("outcome", {}).get("status", "") == "FAIL"),
            "error_count": sum(1 for r in results if r.get("outcome", {}).get("status", "") == "ERROR"),
        },
    }
    report_path = ARTIFACTS_DIR / "evaluation_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\nFull report saved: {report_path}")

    summary = report["summary"]
    print(f"\n{'='*60}")
    print(f"Results: {summary['pass_count']} PASS | {summary['fail_count']} FAIL | {summary['error_count']} ERROR")
    return 0 if summary["fail_count"] == 0 and summary["error_count"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
