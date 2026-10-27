"""System health and diagnostic checks."""

from __future__ import annotations

import sys
from typing import Any, Dict
from evidencepilot.config import AppConfig
from evidencepilot.tools.url_policy import UnsafeURLError, validate_target_url


def check_system_health(config: AppConfig) -> Dict[str, Any]:
    """Inspect environment, configuration, and security policies without leaking secrets."""
    # 1. SSRF Policy verification
    ssrf_status = "VERIFIED_ACTIVE"
    try:
        validate_target_url("http://127.0.0.1:8000", resolve_dns=False)
        ssrf_status = "FAILED_LOCAL_IP_NOT_BLOCKED"
    except UnsafeURLError:
        pass  # Expected safe behavior

    try:
        validate_target_url("http://169.254.169.254/latest", resolve_dns=False)
        ssrf_status = "FAILED_METADATA_NOT_BLOCKED"
    except UnsafeURLError:
        pass  # Expected safe behavior

    # 2. Key presence
    gemini_ready = bool(config.gemini_api_key and config.gemini_api_key.strip())
    tavily_ready = bool(config.tavily_api_key and config.tavily_api_key.strip())

    if gemini_ready and tavily_ready:
        overall_status = "READY_FOR_LIVE_RESEARCH"
    elif gemini_ready or tavily_ready:
        overall_status = "PARTIALLY_CONFIGURED"
    else:
        overall_status = "OFFLINE_TEST_READY (No live API keys configured)"

    return {
        "status": overall_status,
        "python_version": sys.version.split()[0],
        "ssrf_protection": ssrf_status,
        "gemini_configured": gemini_ready,
        "gemini_model": config.gemini_model,
        "tavily_configured": tavily_ready,
        "budgets": {
            "max_search_queries": config.max_search_queries,
            "max_fetch_pages": config.max_fetch_pages,
            "request_timeout_seconds": config.request_timeout_seconds,
        },
        "safe_config_summary": config.safe_summary(),
    }
