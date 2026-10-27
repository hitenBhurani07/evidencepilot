"""Research planner module generating explicit, bounded execution plans."""

from __future__ import annotations

import logging
from typing import List, Optional
from evidencepilot.providers.base import LLMProvider, ProviderError
from evidencepilot.schemas.research import (
    PlanStep,
    ResearchPlan,
    ResearchRequest,
    StepStatus,
    ToolType,
)

logger = logging.getLogger(__name__)

PLANNER_SYSTEM_INSTRUCTION = """You are the research planner for EvidencePilot, an evidence-grounded AI research assistant.
Your job is to formulate a focused, bounded, sequential research plan for a given user query.

Rules for planning:
1. Formulate 2 to 4 distinct, numbered steps.
2. Step 1 must be a 'web_search' with a specific search query designed to discover authoritative sources.
3. Step 2 should be 'fetch_page' to retrieve full readable page content for candidate URLs discovered in search.
4. If the user question requires comparing multiple entities or technical specifics, include an optional secondary 'web_search'.
5. Keep steps practical, efficient, and directly related to the user's research goals.
6. Do NOT exceed 4 steps under any circumstance.
"""


class ResearchPlanner:
    """Creates typed, inspectable research plans using an LLM or deterministic fallback."""

    def __init__(self, llm_provider: LLMProvider, max_steps: int = 4):
        self.llm = llm_provider
        self.max_steps = max_steps

    def create_plan(self, request: ResearchRequest) -> ResearchPlan:
        """Generate a verified, bounded research plan for the request."""
        prompt = (
            f"Research Question: '{request.query}'\n"
            f"Max search query budget: {request.max_search_queries}\n"
            f"Max pages to fetch budget: {request.max_pages_to_fetch}\n"
            "Create a clean, bounded ResearchPlan with 2-4 sequential steps."
        )

        try:
            plan = self.llm.generate_structured(
                prompt=prompt,
                schema_class=ResearchPlan,
                system_instruction=PLANNER_SYSTEM_INSTRUCTION,
            )
            return self._enforce_plan_bounds(plan, request)
        except (ProviderError, Exception) as exc:
            logger.warning("LLM planner invocation failed (%s). Generating deterministic fallback plan.", exc)
            return self.create_fallback_plan(request, reason=f"Fallback due to planner error: {exc}")

    def create_fallback_plan(self, request: ResearchRequest, reason: str = "Deterministic default plan") -> ResearchPlan:
        """Create a deterministic baseline plan when LLM is unavailable or fails."""
        steps: List[PlanStep] = [
            PlanStep(
                step_number=1,
                tool=ToolType.WEB_SEARCH,
                goal=f"Discover authoritative sources answering: '{request.query}'",
                action_input=request.query,
                status=StepStatus.PENDING,
            ),
            PlanStep(
                step_number=2,
                tool=ToolType.FETCH_PAGE,
                goal="Extract detailed page content from top discovered search results",
                action_input="top_search_urls",
                status=StepStatus.PENDING,
            ),
            PlanStep(
                step_number=3,
                tool=ToolType.QUALITY_FILTER,
                goal="Filter duplicates, score source credibility, and cap source budget",
                action_input="all_gathered_sources",
                status=StepStatus.PENDING,
            ),
        ]

        return ResearchPlan(
            question=request.query,
            rationale=reason,
            steps=steps,
            estimated_search_queries=1,
            estimated_target_urls=request.max_pages_to_fetch,
        )

    def _enforce_plan_bounds(self, plan: ResearchPlan, request: ResearchRequest) -> ResearchPlan:
        """Sanitize and constrain plan steps to prevent cost/latency runaway."""
        # 1. Cap steps
        bounded_steps = plan.steps[:self.max_steps]
        
        # 2. Re-index cleanly and reset status
        for idx, step in enumerate(bounded_steps, start=1):
            step.step_number = idx
            step.status = StepStatus.PENDING

        plan.steps = bounded_steps
        plan.question = request.query
        return plan
