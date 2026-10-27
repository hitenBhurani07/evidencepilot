"""Workflow event emission and tracking for agent observability."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field


class WorkflowEventType(str, Enum):
    """Categorized workflow events during research execution."""
    REQUEST_VALIDATED = "request_validated"
    PLAN_CREATED = "plan_created"
    STEP_STARTED = "step_started"
    TOOL_CALLED = "tool_called"
    TOOL_COMPLETED = "tool_completed"
    TOOL_FAILED = "tool_failed"
    EVIDENCE_FILTERED = "evidence_filtered"
    SYNTHESIS_STARTED = "synthesis_started"
    SYNTHESIS_COMPLETED = "synthesis_completed"
    RUN_COMPLETED = "run_completed"
    RUN_FAILED = "run_failed"


class WorkflowEvent(BaseModel):
    """A discrete observable event emitted during research orchestration."""
    
    event_type: WorkflowEventType
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    step_number: Optional[int] = None
    tool_name: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)


EventHandler = Callable[[WorkflowEvent], None]


class EventBus:
    """Simple in-memory event bus to notify subscribers and retain execution event history."""
    
    def __init__(self, listener: Optional[EventHandler] = None):
        self._listener = listener
        self.history: List[WorkflowEvent] = []

    def emit(
        self,
        event_type: WorkflowEventType,
        message: str,
        step_number: Optional[int] = None,
        tool_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> WorkflowEvent:
        """Record and dispatch an event."""
        event = WorkflowEvent(
            event_type=event_type,
            message=message,
            step_number=step_number,
            tool_name=tool_name,
            details=details or {},
        )
        self.history.append(event)
        if self._listener is not None:
            try:
                self._listener(event)
            except Exception:
                # Listener failures must never crash agent execution
                pass
        return event
