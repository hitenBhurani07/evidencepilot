"""Tests for application configuration, validation, and secret masking."""

import pytest
from evidencepilot.config import AppConfig, ConfigError, mask_secret


def test_mask_secret_none_or_empty():
    assert mask_secret(None) == "[NOT SET]"
    assert mask_secret("") == "[NOT SET]"
    assert mask_secret("   ") == "[NOT SET]"


def test_mask_secret_redacts_properly():
    secret = "AIzaSyFakeKeyForTesting123456789"
    masked = mask_secret(secret)
    # Ensure full secret is never in the masked output
    assert secret not in masked
    assert "AIza" in masked
    assert "89" in masked
    assert f"len={len(secret)}" in masked


def test_mask_secret_short_values():
    short_secret = "secret1"
    masked = mask_secret(short_secret)
    assert short_secret not in masked
    assert f"len={len(short_secret)}" in masked


def test_config_defaults_and_safe_summary(monkeypatch):
    # Ensure clean environment without accidental keys
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    
    cfg = AppConfig.load(env_path="nonexistent_test.env")
    assert cfg.gemini_api_key is None
    assert cfg.tavily_api_key is None
    assert cfg.gemini_model == "gemini-2.5-flash"
    assert cfg.max_search_queries == 3
    assert cfg.max_fetch_pages == 5
    assert cfg.request_timeout_seconds == 15

    summary = cfg.safe_summary()
    assert summary["gemini_api_key"] == "[NOT SET]"
    assert summary["tavily_api_key"] == "[NOT SET]"
    assert summary["gemini_model"] == "gemini-2.5-flash"


def test_live_validation_fails_safely_when_keys_missing(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    
    cfg = AppConfig(gemini_api_key=None, tavily_api_key=None)
    
    with pytest.raises(ConfigError) as exc_gemini:
        cfg.validate_for_live_llm()
    assert "Missing GEMINI_API_KEY" in str(exc_gemini.value)
    assert "docs/FREE_API_SETUP_GUIDE.md" in str(exc_gemini.value)
    
    with pytest.raises(ConfigError) as exc_tavily:
        cfg.validate_for_live_search()
    assert "Missing TAVILY_API_KEY" in str(exc_tavily.value)
    assert "docs/FREE_API_SETUP_GUIDE.md" in str(exc_tavily.value)


def test_live_validation_succeeds_when_keys_present():
    cfg = AppConfig(
        gemini_api_key="dummy_gemini_key_12345",
        tavily_api_key="tvly-dummy_tavily_key_12345"
    )
    # Should not raise any error
    cfg.validate_for_live_llm()
    cfg.validate_for_live_search()
    
    summary = cfg.safe_summary()
    # Ensure secrets are masked in summary
    assert "dummy_gemini_key_12345" not in summary["gemini_api_key"]
    assert "tvly-dummy_tavily_key_12345" not in summary["tavily_api_key"]
