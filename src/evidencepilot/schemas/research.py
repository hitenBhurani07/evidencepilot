"""Core domain schemas for EvidencePilot research workflows."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl, field_validator


class ToolType(str, Enum):
    """Supported tools for agent planning and execution."""
    WEB_SEARCH = "web_search"
    FETCH_PAGE = "fetch_page"
    QUALITY_FILTER = "quality_filter"


class StepStatus(str, Enum):
    """Execution status for an individual plan step."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ResearchRequest(BaseModel):
    """User input request for a research task."""
    
    query: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="The research question or topic to investigate."
    )
    max_search_queries: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Maximum search queries to generate and execute."
    )
    max_pages_to_fetch: int = Field(
        default=4,
        ge=1,
        le=8,
        description="Maximum individual web pages to fetch and extract content from."
    )
    require_confidence_threshold: float = Field(
        default=0.4,
        ge=0.0,
        le=1.0,
        description="Minimum confidence required to avoid low-evidence warning fallback."
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Research query cannot be empty or whitespace only.")
        return cleaned


class PlanStep(BaseModel):
    """A discrete step in an explicit research plan."""
    
    step_number: int = Field(..., ge=1, le=15)
    tool: ToolType = Field(..., description="Tool to invoke in this step.")
    goal: str = Field(..., min_length=3, max_length=200, description="Purpose of this step.")
    action_input: str = Field(..., min_length=1, max_length=300, description="Search query or URL target.")
    status: StepStatus = Field(default=StepStatus.PENDING)
    result_summary: Optional[str] = Field(default=None, max_length=500)


class ResearchPlan(BaseModel):
    """The visible, inspectable plan generated before executing tools."""
    
    question: str = Field(..., description="Original user research question.")
    rationale: str = Field(..., max_length=1000, description="Why this planning sequence was chosen.")
    steps: List[PlanStep] = Field(..., min_length=1, max_length=10)
    estimated_search_queries: int = Field(default=1, ge=1, le=5)
    estimated_target_urls: int = Field(default=2, ge=0, le=10)


class SourceItem(BaseModel):
    """Normalized evidence source gathered during research."""
    
    id: str = Field(..., description="Unique source identifier within run, e.g. S1, S2.")
    url: str = Field(..., description="Canonical source URL.")
    title: str = Field(..., min_length=1, max_length=300)
    snippet: str = Field(default="", max_length=1500)
    full_content: Optional[str] = Field(default=None, description="Extracted text from page (if fetched).")
    domain: str = Field(default="", description="Registered host domain.")
    quality_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Calculated source credibility score.")
    is_filtered_out: bool = Field(default=False, description="True if marked duplicate or low value.")
    filter_reason: Optional[str] = Field(default=None)


class Finding(BaseModel):
    """A synthesized finding backed by specific source IDs."""
    
    statement: str = Field(..., min_length=5, max_length=1000)
    source_ids: List[str] = Field(
        default_factory=list,
        description="IDs of sources supporting this statement (e.g. ['S1', 'S2'])."
    )
    confidence: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Confidence in this specific statement based on evidence strength."
    )


class RunMetadata(BaseModel):
    """Observability metadata for the research run."""
    
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: Optional[datetime] = None
    total_latency_seconds: Optional[float] = None
    model_name: str = Field(default="unknown")
    search_provider: str = Field(default="unknown")
    tool_calls_count: Dict[str, int] = Field(default_factory=dict)
    total_sources_found: int = Field(default=0)
    sources_used_in_synthesis: int = Field(default=0)
    is_mock_run: bool = Field(default=False)


class StructuredAnswer(BaseModel):
    """The complete, validated final answer complying with all assignment requirements."""
    
    question: str = Field(..., description="Original user question.")
    short_answer: str = Field(
        ...,
        min_length=10,
        max_length=1500,
        description="Direct, executive summary response answering the core query."
    )
    key_findings: List[Finding] = Field(
        ...,
        min_length=1,
        max_length=15,
        description="Bullet-point findings explicitly linked to evidence sources."
    )
    sources: List[SourceItem] = Field(
        ...,
        description="All validated sources gathered and considered during this research."
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall confidence in the answer grounded in evidence quality and completeness."
    )
    confidence_rationale: str = Field(
        ...,
        min_length=5,
        max_length=1000,
        description="Explanation of why this confidence score was assigned."
    )
    assumptions: List[str] = Field(
        default_factory=list,
        description="Explicit assumptions made in interpreting query or incomplete evidence."
    )
    limitations: List[str] = Field(
        default_factory=list,
        description="Blind spots, potential freshness issues, missing data, or provider limits."
    )
    next_steps: List[str] = Field(
        default_factory=list,
        description="Suggested further questions, deeper investigations, or verification steps."
    )
    metadata: RunMetadata = Field(
        default_factory=RunMetadata,
        description="Execution and observability statistics."
    )
