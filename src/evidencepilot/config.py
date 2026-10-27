"""Application configuration with safe secret handling and validation."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field


def mask_secret(secret: Optional[str]) -> str:
    """Safely mask a secret for logs and error messages.
    
    Never outputs the full secret or any identifiable plaintext.
    """
    if not secret or not secret.strip():
        return "[NOT SET]"
    cleaned = secret.strip()
    if len(cleaned) <= 8:
        return f"[SET (len={len(cleaned)}) ***]"
    return f"[SET (len={len(cleaned)}) {cleaned[:4]}...{cleaned[-2:]}]"


class ConfigError(ValueError):
    """Raised when configuration is invalid or missing required keys."""
    pass


class AppConfig(BaseModel):
    """Environment configuration settings for EvidencePilot."""
    
    gemini_api_key: Optional[str] = Field(default=None, description="Google Gemini API key")
    gemini_model: str = Field(
        default="gemini-2.5-flash",
        description="Gemini model identifier (defaulting to current AI Studio free-tier model)"
    )
    tavily_api_key: Optional[str] = Field(default=None, description="Tavily search API key")
    
    app_env: str = Field(default="development", description="Application environment")
    log_level: str = Field(default="INFO", description="Log level")
    
    max_search_queries: int = Field(default=3, ge=1, le=10, description="Max search queries per research run")
    max_fetch_pages: int = Field(default=5, ge=1, le=15, description="Max web pages to fetch per research run")
    request_timeout_seconds: int = Field(default=15, ge=2, le=60, description="HTTP request timeout in seconds")
    
    model_config = {
        "extra": "ignore",
    }

    @classmethod
    def load(cls, env_path: Optional[str | Path] = None) -> AppConfig:
        """Load configuration from environment, optionally loading from a .env file."""
        if env_path is not None:
            path = Path(env_path)
            if path.exists():
                load_dotenv(dotenv_path=path, override=True)
        else:
            # Look for .env in current directory or project root
            if Path(".env").exists():
                load_dotenv(dotenv_path=".env", override=False)
                
        return cls(
            gemini_api_key=os.getenv("GEMINI_API_KEY") or None,
            gemini_model=os.getenv("GEMINI_MODEL") or "gemini-2.5-flash",
            tavily_api_key=os.getenv("TAVILY_API_KEY") or None,
            app_env=os.getenv("APP_ENV", "development"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            max_search_queries=int(os.getenv("MAX_SEARCH_QUERIES", "3")),
            max_fetch_pages=int(os.getenv("MAX_FETCH_PAGES", "5")),
            request_timeout_seconds=int(os.getenv("REQUEST_TIMEOUT_SECONDS", "15")),
        )

    def validate_for_live_llm(self) -> None:
        """Verify that Gemini credentials are configured before making live LLM calls."""
        if not self.gemini_api_key or not self.gemini_api_key.strip():
            raise ConfigError(
                "Missing GEMINI_API_KEY. Live LLM synthesis is not configured. "
                "See docs/FREE_API_SETUP_GUIDE.md for safe setup instructions. "
                "(Status: credential is not set in local environment)"
            )

    def validate_for_live_search(self) -> None:
        """Verify that Tavily credentials are configured before making live search calls."""
        if not self.tavily_api_key or not self.tavily_api_key.strip():
            raise ConfigError(
                "Missing TAVILY_API_KEY. Live web search is not configured. "
                "See docs/FREE_API_SETUP_GUIDE.md for safe setup instructions. "
                "(Status: credential is not set in local environment)"
            )

    def safe_summary(self) -> Dict[str, Any]:
        """Return a dictionary of configuration settings with all secrets safely masked."""
        return {
            "gemini_api_key": mask_secret(self.gemini_api_key),
            "gemini_model": self.gemini_model,
            "tavily_api_key": mask_secret(self.tavily_api_key),
            "app_env": self.app_env,
            "log_level": self.log_level,
            "max_search_queries": self.max_search_queries,
            "max_fetch_pages": self.max_fetch_pages,
            "request_timeout_seconds": self.request_timeout_seconds,
        }
