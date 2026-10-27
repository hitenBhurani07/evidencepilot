"""Structured per-run observability logger.

Emits one-line JSON log entries for each significant event in a research run.
Run ID, stage, timing, and counts are always present; the query text is NOT
logged by default to avoid inadvertent privacy exposure.
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from typing import Any, Dict, Optional

from evidencepilot.logging import SecretMaskingFilter

_root_logger = logging.getLogger(__name__)


class RunLogger:
    """Structured logger bound to a single research run.

    Each call to a stage method emits a JSON-serialisable log record with:
    - run_id   : unique ID for this execution (UUID4, generated at construction)
    - stage    : descriptive stage name (e.g. "search", "fetch", "synthesis")
    - event    : specific event type (e.g. "started", "completed", "failed")
    - elapsed_s: wall-clock seconds since run_id was created
    - counts   : optional key→int mapping for tool invocation/source counts
    - error    : sanitised error category string (never raw exception text)
    - detail   : any additional structured metadata (no user data by default)
    """

    def __init__(
        self,
        run_id: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.run_id: str = run_id or str(uuid.uuid4())
        self._logger = logger or _root_logger
        self._start: float = time.monotonic()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def log_start(self, query_length: int) -> None:
        """Emit run-started event (query text intentionally excluded)."""
        self._emit(
            stage="run",
            event="started",
            detail={"query_chars": query_length},
        )

    def log_plan(self, steps_count: int, rationale_chars: int) -> None:
        """Log plan creation."""
        self._emit(
            stage="planner",
            event="plan_created",
            counts={"steps": steps_count},
            detail={"rationale_chars": rationale_chars},
        )

    def log_search(self, event: str, sources_found: int = 0, query_index: int = 0) -> None:
        """Log a search step event."""
        self._emit(
            stage="search",
            event=event,
            counts={"query_index": query_index, "sources_found": sources_found},
        )

    def log_fetch(self, event: str, url_count: int = 0, success_count: int = 0) -> None:
        """Log a page-fetch step event."""
        self._emit(
            stage="fetch",
            event=event,
            counts={"urls_attempted": url_count, "succeeded": success_count},
        )

    def log_filter(self, kept: int, filtered: int) -> None:
        """Log source quality filter results."""
        self._emit(
            stage="filter",
            event="completed",
            counts={"kept": kept, "filtered": filtered},
        )

    def log_synthesis(self, event: str, sources_count: int = 0) -> None:
        """Log synthesis events."""
        self._emit(
            stage="synthesis",
            event=event,
            counts={"sources": sources_count},
        )

    def log_error(self, stage: str, error_category: str, is_retryable: bool = True) -> None:
        """Log a sanitised error event (never raw exception text or keys)."""
        self._emit(
            stage=stage,
            event="error",
            error=error_category,
            detail={"retryable": is_retryable},
        )

    def log_complete(
        self,
        confidence: float,
        total_sources: int,
        sources_used: int,
        tool_calls: Dict[str, int],
    ) -> None:
        """Emit final run-completed event with summary stats."""
        self._emit(
            stage="run",
            event="completed",
            counts={
                "total_sources_found": total_sources,
                "sources_used": sources_used,
                **tool_calls,
            },
            detail={"confidence_score": round(confidence, 3)},
        )

    def log_failed(self, error_category: str) -> None:
        """Emit run-failed event."""
        self._emit(
            stage="run",
            event="failed",
            error=error_category,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _emit(
        self,
        stage: str,
        event: str,
        counts: Optional[Dict[str, int]] = None,
        error: Optional[str] = None,
        detail: Optional[Dict[str, Any]] = None,
    ) -> None:
        record: Dict[str, Any] = {
            "run_id": self.run_id,
            "stage": stage,
            "event": event,
            "elapsed_s": round(time.monotonic() - self._start, 3),
        }
        if counts:
            record["counts"] = counts
        if error:
            record["error"] = error
        if detail:
            record["detail"] = detail

        # Serialize to JSON and pass through secret masking
        raw = json.dumps(record, separators=(",", ":"))
        sanitised = SecretMaskingFilter.mask_text(raw)
        self._logger.info(sanitised)
