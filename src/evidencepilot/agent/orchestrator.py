"""Research agent orchestrator executing plans and managing tool flows."""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from evidencepilot.agent.events import EventBus, WorkflowEventType
from evidencepilot.agent.planner import ResearchPlanner
from evidencepilot.agent.synthesizer import ResearchSynthesizer
from evidencepilot.providers.base import LLMProvider, SearchProvider
from evidencepilot.providers.fakes import FakeLLMProvider, FakeSearchProvider
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
from evidencepilot.tools.extractor import ExtractionResult, PageExtractor
from evidencepilot.tools.search import SearchTool
from evidencepilot.tools.source_scorer import SourceQualityFilter

logger = logging.getLogger(__name__)


class ResearchOrchestrator:
    """Coordinates research planning, tool execution, evidence hygiene, and synthesis."""

    def __init__(
        self,
        llm_provider: LLMProvider,
        search_provider: SearchProvider,
        extractor: Optional[PageExtractor] = None,
        quality_filter: Optional[SourceQualityFilter] = None,
        planner: Optional[ResearchPlanner] = None,
        event_bus: Optional[EventBus] = None,
        synthesizer: Optional[Callable[[ResearchRequest, List[SourceItem], RunMetadata], StructuredAnswer]] = None,
    ):
        self.llm = llm_provider
        self.search_provider = search_provider
        self.extractor = extractor or PageExtractor()
        self.quality_filter = quality_filter or SourceQualityFilter()
        self.planner = planner or ResearchPlanner(llm_provider=self.llm)
        self.event_bus = event_bus or EventBus()
        self.search_tool = SearchTool(provider=self.search_provider)
        self.synthesizer = synthesizer or (lambda req, src, meta: ResearchSynthesizer(self.llm).synthesize(req, src, meta))

    def execute(self, request: ResearchRequest) -> StructuredAnswer:
        """Run the end-to-end research workflow."""
        start_time = time.time()
        start_dt = datetime.now(timezone.utc)
        
        is_mock = isinstance(self.llm, FakeLLMProvider) or isinstance(self.search_provider, FakeSearchProvider)
        metadata = RunMetadata(
            started_at=start_dt,
            model_name=getattr(self.llm, "model_name", "fake_llm"),
            search_provider=self.search_provider.__class__.__name__,
            is_mock_run=is_mock,
            tool_calls_count={"web_search": 0, "fetch_page": 0, "quality_filter": 0},
        )

        self.event_bus.emit(
            WorkflowEventType.REQUEST_VALIDATED,
            f"Validated query: '{request.query}'",
            details={"query": request.query, "is_mock_run": is_mock},
        )

        # 1. Generate Plan
        plan = self.planner.create_plan(request)
        self.event_bus.emit(
            WorkflowEventType.PLAN_CREATED,
            f"Plan formulated with {len(plan.steps)} steps: {plan.rationale}",
            details={"steps_count": len(plan.steps), "rationale": plan.rationale},
        )

        all_sources: List[SourceItem] = []
        search_queries_run = 0
        pages_fetched = 0

        # 2. Execute Plan Steps
        for step in plan.steps:
            self.event_bus.emit(
                WorkflowEventType.STEP_STARTED,
                f"Starting Step {step.step_number} [{step.tool.value}]: {step.goal}",
                step_number=step.step_number,
                tool_name=step.tool.value,
            )
            step.status = StepStatus.RUNNING

            try:
                if step.tool == ToolType.WEB_SEARCH:
                    if search_queries_run >= request.max_search_queries:
                        step.status = StepStatus.SKIPPED
                        step.result_summary = "Skipped: Search query budget exhausted"
                        continue

                    query_to_run = step.action_input if step.action_input else request.query
                    metadata.tool_calls_count["web_search"] += 1
                    search_queries_run += 1

                    self.event_bus.emit(
                        WorkflowEventType.TOOL_CALLED,
                        f"Executing web search: '{query_to_run}'",
                        step_number=step.step_number,
                        tool_name="web_search",
                        details={"query": query_to_run},
                    )

                    new_sources = self.search_tool.execute(
                        query=query_to_run,
                        max_results=5,
                        start_index=len(all_sources) + 1,
                    )
                    all_sources.extend(new_sources)
                    step.status = StepStatus.COMPLETED
                    step.result_summary = f"Discovered {len(new_sources)} raw sources"

                    self.event_bus.emit(
                        WorkflowEventType.TOOL_COMPLETED,
                        f"Web search completed; found {len(new_sources)} sources",
                        step_number=step.step_number,
                        tool_name="web_search",
                        details={"new_sources_count": len(new_sources)},
                    )

                elif step.tool == ToolType.FETCH_PAGE:
                    # Determine target candidate URLs to fetch
                    unfetched = [s for s in all_sources if not s.full_content and not s.is_filtered_out]
                    urls_to_fetch = [s.url for s in unfetched[:request.max_pages_to_fetch - pages_fetched]]

                    if not urls_to_fetch:
                        step.status = StepStatus.SKIPPED
                        step.result_summary = "No candidate URLs available to fetch"
                        continue

                    extracted_count = 0
                    for url in urls_to_fetch:
                        metadata.tool_calls_count["fetch_page"] += 1
                        pages_fetched += 1

                        self.event_bus.emit(
                            WorkflowEventType.TOOL_CALLED,
                            f"Fetching page content: {url}",
                            step_number=step.step_number,
                            tool_name="fetch_page",
                            details={"url": url},
                        )

                        result: ExtractionResult = self.extractor.extract(url)
                        if result.is_success and result.content:
                            # Attach full content to matching source
                            for s in all_sources:
                                if s.url == url or s.url == result.url:
                                    s.full_content = result.content
                                    if result.title:
                                        s.title = result.title
                            extracted_count += 1
                            self.event_bus.emit(
                                WorkflowEventType.TOOL_COMPLETED,
                                f"Extracted {len(result.content)} chars from {url}",
                                step_number=step.step_number,
                                tool_name="fetch_page",
                                details={"url": url, "chars": len(result.content)},
                            )
                        else:
                            self.event_bus.emit(
                                WorkflowEventType.TOOL_FAILED,
                                f"Failed to extract {url}: {result.error_message}",
                                step_number=step.step_number,
                                tool_name="fetch_page",
                                details={"url": url, "error": result.error_message},
                            )

                    step.status = StepStatus.COMPLETED
                    step.result_summary = f"Fetched content for {extracted_count}/{len(urls_to_fetch)} URLs"

                elif step.tool == ToolType.QUALITY_FILTER:
                    metadata.tool_calls_count["quality_filter"] += 1
                    self.event_bus.emit(
                        WorkflowEventType.TOOL_CALLED,
                        "Processing source deduplication and quality scoring",
                        step_number=step.step_number,
                        tool_name="quality_filter",
                    )
                    kept, filtered = self.quality_filter.process(all_sources)
                    all_sources = kept
                    step.status = StepStatus.COMPLETED
                    step.result_summary = f"Retained {len(kept)} sources; filtered {len(filtered)}"
                    self.event_bus.emit(
                        WorkflowEventType.EVIDENCE_FILTERED,
                        f"Retained {len(kept)} top quality sources, filtered {len(filtered)}",
                        step_number=step.step_number,
                        details={"kept_count": len(kept), "filtered_count": len(filtered)},
                    )

            except Exception as step_exc:
                logger.error("Error executing Step %s (%s): %s", step.step_number, step.tool.value, step_exc)
                step.status = StepStatus.FAILED
                step.result_summary = f"Step failed: {step_exc}"
                self.event_bus.emit(
                    WorkflowEventType.TOOL_FAILED,
                    f"Step {step.step_number} failed: {step_exc}",
                    step_number=step.step_number,
                    tool_name=step.tool.value,
                    details={"error": str(step_exc)},
                )

        # 3. Always run final source hygiene pass if not already done
        metadata.total_sources_found = len(all_sources)
        kept_sources, filtered_sources = self.quality_filter.process(all_sources)
        metadata.sources_used_in_synthesis = len(kept_sources)

        # 4. Handle Total Tool Failure / Zero Evidence Case
        if not kept_sources:
            return self._build_zero_evidence_response(request, metadata, start_time)

        # 5. Synthesize Structured Answer
        self.event_bus.emit(
            WorkflowEventType.SYNTHESIS_STARTED,
            f"Synthesizing structured answer grounded in {len(kept_sources)} sources",
            details={"sources_count": len(kept_sources)},
        )

        if self.synthesizer is not None:
            answer = self.synthesizer(request, kept_sources, metadata)
        else:
            answer = self._synthesize_fallback_structured(request, kept_sources, metadata)

        # 6. Finalize Run Metadata
        end_time = time.time()
        metadata.finished_at = datetime.now(timezone.utc)
        metadata.total_latency_seconds = round(end_time - start_time, 2)
        answer.metadata = metadata

        self.event_bus.emit(
            WorkflowEventType.RUN_COMPLETED,
            f"Research complete in {metadata.total_latency_seconds}s with confidence {answer.confidence_score}",
            details={"latency_seconds": metadata.total_latency_seconds, "confidence": answer.confidence_score},
        )
        return answer

    def _build_zero_evidence_response(
        self,
        request: ResearchRequest,
        metadata: RunMetadata,
        start_time: float,
    ) -> StructuredAnswer:
        """Return an explicit, structured refusal when zero valid sources were obtained."""
        end_time = time.time()
        metadata.finished_at = datetime.now(timezone.utc)
        metadata.total_latency_seconds = round(end_time - start_time, 2)

        self.event_bus.emit(
            WorkflowEventType.RUN_FAILED,
            "Research failed to gather verified evidence; returning structured low-confidence refusal.",
            details={"latency_seconds": metadata.total_latency_seconds},
        )

        return StructuredAnswer(
            question=request.query,
            short_answer="No verifiable evidence could be gathered to answer this question. Tools returned no authoritative results or encountered network/provider errors.",
            key_findings=[
                Finding(
                    statement="Evidence gathering returned zero qualifying sources. The agent refuses to synthesize ungrounded answers.",
                    source_ids=[],
                    confidence=0.0,
                )
            ],
            sources=[],
            confidence_score=0.0,
            confidence_rationale="Zero verified sources were gathered. High-reliability policy forbids fabricating claims.",
            assumptions=["External web search or page retrieval yielded no accessible evidence."],
            limitations=["No online sources were available for this specific query during execution."],
            next_steps=[
                "Check network connection and search provider credentials.",
                "Rephrase the question with broader search keywords.",
            ],
            metadata=metadata,
        )

    def _synthesize_fallback_structured(
        self,
        request: ResearchRequest,
        sources: List[SourceItem],
        metadata: RunMetadata,
    ) -> StructuredAnswer:
        """Baseline structured synthesis using available sources when custom synthesizer is omitted."""
        findings = [
            Finding(
                statement=f"Discovered relevant evidence from {s.domain}: {s.snippet[:150]}...",
                source_ids=[s.id],
                confidence=round(s.quality_score, 2),
            )
            for s in sources[:3]
        ]

        avg_quality = sum(s.quality_score for s in sources) / max(1, len(sources))

        return StructuredAnswer(
            question=request.query,
            short_answer=f"Synthesized research summary for '{request.query}' based on {len(sources)} verified sources.",
            key_findings=findings,
            sources=sources,
            confidence_score=round(avg_quality, 2),
            confidence_rationale=f"Confidence computed directly from {len(sources)} verified sources with mean credibility score {round(avg_quality, 2)}.",
            assumptions=["Retrieved sources represent current factual state."],
            limitations=["Limited to top search results; full web crawl not conducted."],
            next_steps=["Examine individual source URLs for deeper technical nuances."],
            metadata=metadata,
        )
