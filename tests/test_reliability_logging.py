"""Stage 06 — Reliability, security, and structured logging tests.

Tests that are NOT already in test_security.py:
- RunLogger emits structured JSON with required fields (run_id, stage, event, elapsed_s)
- RunLogger never logs raw query text
- RunLogger redacts secret patterns embedded in detail fields
- Overall run timeout budget is respected via config
- Common API errors produce readable, non-credential-leaking messages
- .env and secret files are excluded from git
"""

from __future__ import annotations

import json
import logging
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

from evidencepilot.config import AppConfig, mask_secret
from evidencepilot.providers.base import AuthError, NetworkError, RateLimitError
from evidencepilot.run_logger import RunLogger


# ---------------------------------------------------------------------------
# Structured logging — RunLogger
# ---------------------------------------------------------------------------


class LogCapture(logging.Handler):
    """In-memory log handler that collects all records."""

    def __init__(self):
        super().__init__()
        self.records: list[logging.LogRecord] = []
        self.lines: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)
        self.lines.append(self.format(record))


def _make_run_logger() -> tuple[RunLogger, LogCapture]:
    """Create a RunLogger wired to an in-memory capture handler."""
    inner_logger = logging.getLogger(f"test_run_{id(object())}")
    inner_logger.setLevel(logging.DEBUG)
    inner_logger.propagate = False
    capture = LogCapture()
    inner_logger.addHandler(capture)
    rl = RunLogger(run_id="test-run-0001", logger=inner_logger)
    return rl, capture


def test_run_logger_emits_json_with_required_fields():
    """RunLogger output must be parseable JSON with run_id, stage, event, elapsed_s."""
    rl, cap = _make_run_logger()
    rl.log_start(query_length=42)

    assert len(cap.lines) == 1
    msg = cap.lines[0]
    data = json.loads(msg)

    assert data["run_id"] == "test-run-0001"
    assert data["stage"] == "run"
    assert data["event"] == "started"
    assert "elapsed_s" in data
    assert isinstance(data["elapsed_s"], float)


def test_run_logger_does_not_log_query_text():
    """Query text must never appear in a RunLogger record (privacy protection)."""
    rl, cap = _make_run_logger()
    sensitive_query = "secret internal research topic"
    # log_start only receives the length, not the text
    rl.log_start(query_length=len(sensitive_query))

    for line in cap.lines:
        assert sensitive_query not in line, "Query text must not appear in structured log"


def test_run_logger_log_search_has_counts():
    rl, cap = _make_run_logger()
    rl.log_search(event="completed", sources_found=5, query_index=1)

    data = json.loads(cap.lines[-1])
    assert data["stage"] == "search"
    assert data["event"] == "completed"
    assert data["counts"]["sources_found"] == 5


def test_run_logger_log_fetch_has_counts():
    rl, cap = _make_run_logger()
    rl.log_fetch(event="completed", url_count=3, success_count=2)

    data = json.loads(cap.lines[-1])
    assert data["stage"] == "fetch"
    assert data["counts"]["succeeded"] == 2


def test_run_logger_log_complete():
    rl, cap = _make_run_logger()
    rl.log_complete(
        confidence=0.82,
        total_sources=8,
        sources_used=5,
        tool_calls={"web_search": 2, "fetch_page": 3},
    )
    data = json.loads(cap.lines[-1])
    assert data["event"] == "completed"
    assert data["detail"]["confidence_score"] == 0.82
    assert data["counts"]["total_sources_found"] == 8


def test_run_logger_log_error_includes_category():
    rl, cap = _make_run_logger()
    rl.log_error(stage="search", error_category="rate_limit", is_retryable=True)

    data = json.loads(cap.lines[-1])
    assert data["error"] == "rate_limit"
    assert data["detail"]["retryable"] is True


def test_run_logger_redacts_secrets_in_output():
    """If a secret accidentally reaches the RunLogger, it should be masked."""
    rl, cap = _make_run_logger()
    # Force a detail dict that contains a key-like value
    rl._emit(
        stage="test",
        event="leak_attempt",
        detail={"bad_key": "AIzaSyABCDEFGHIJKLMNOPQRSTUVWXYZ12345"},
    )
    assert "AIzaSyABCDEFGHIJKLMNOPQRSTUVWXYZ12345" not in cap.lines[-1]
    assert "[REDACTED_SECRET]" in cap.lines[-1]


def test_run_logger_unique_run_ids():
    """Each RunLogger instance must generate a unique run_id."""
    rl1 = RunLogger()
    rl2 = RunLogger()
    assert rl1.run_id != rl2.run_id


# ---------------------------------------------------------------------------
# Config budget guardrails
# ---------------------------------------------------------------------------


def test_config_budget_limits_enforced():
    """AppConfig must clamp budget fields within documented safe limits."""
    cfg = AppConfig(
        max_search_queries=3,
        max_fetch_pages=5,
        request_timeout_seconds=15,
    )
    assert 1 <= cfg.max_search_queries <= 10
    assert 1 <= cfg.max_fetch_pages <= 15
    assert 2 <= cfg.request_timeout_seconds <= 60


def test_config_rejects_out_of_bounds_budget():
    """AppConfig must reject values that violate field bounds."""
    with pytest.raises(Exception):
        AppConfig(max_search_queries=99)


# ---------------------------------------------------------------------------
# Readable error messages for common provider failures
# ---------------------------------------------------------------------------


def test_auth_error_message_is_readable_and_safe():
    """AuthError message must be human-readable and must not contain raw credentials."""
    err = AuthError("Invalid API key or permissions rejected.", provider_name="gemini", status_code=401)
    msg = str(err)
    assert "gemini" in msg.lower() or "401" in msg or "invalid" in msg.lower()
    # The raw key string must not be in the message
    fake_key = "AIzaSyFakeKey1234567890abcdefghijklmno"
    assert fake_key not in msg


def test_rate_limit_error_message_is_readable():
    err = RateLimitError("Quota or rate limit exceeded.", provider_name="tavily", status_code=429)
    msg = str(err)
    assert "rate" in msg.lower() or "quota" in msg.lower() or "429" in msg


def test_network_error_message_is_readable():
    err = NetworkError("Request timed out after 15s", provider_name="gemini")
    msg = str(err)
    assert "timeout" in msg.lower() or "timed" in msg.lower() or "network" in msg.lower()


def test_gemini_provider_maps_auth_error():
    """GeminiProvider must map 401-type exceptions to AuthError with no key leakage."""
    from evidencepilot.providers.gemini import GeminiProvider

    provider = GeminiProvider(api_key="AIzaSyFakeKey1234567890abcdefghijklmno")
    fake_exc = Exception("401 UNAUTHENTICATED: API key not valid. Please pass a valid API key.")
    mapped = provider._map_exception(fake_exc)

    assert isinstance(mapped, AuthError)
    # Key must not appear in sanitized error message
    assert "AIzaSyFakeKey1234567890abcdefghijklmno" not in str(mapped)


def test_gemini_provider_maps_rate_limit_error():
    from evidencepilot.providers.gemini import GeminiProvider

    provider = GeminiProvider(api_key="AIzaSyFakeKey1234567890abcdefghijklmno")
    fake_exc = Exception("429 resource_exhausted: Quota exceeded for quota group")
    mapped = provider._map_exception(fake_exc)

    assert isinstance(mapped, RateLimitError)


def test_gemini_provider_maps_timeout_error():
    from evidencepilot.providers.gemini import GeminiProvider

    provider = GeminiProvider(api_key="AIzaSyFakeKey1234567890abcdefghijklmno")
    fake_exc = Exception("connection timeout during request")
    mapped = provider._map_exception(fake_exc)

    assert isinstance(mapped, NetworkError)


# ---------------------------------------------------------------------------
# Git ignore verification — secrets must not be commitable
# ---------------------------------------------------------------------------


def test_gitignore_excludes_dot_env(tmp_path):
    """Verify that the .gitignore pattern for .env is documented and present."""
    import subprocess
    result = subprocess.run(
        ["git", "check-ignore", "-v", ".env"],
        capture_output=True,
        text=True,
        cwd=r"c:\Users\hiten\prexidion_ai",
    )
    # git check-ignore exits 0 if the file IS ignored, 1 if it is not
    assert result.returncode == 0, (
        f".env is NOT listed in .gitignore! Secrets would be committed to git.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
