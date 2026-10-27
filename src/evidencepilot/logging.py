"""Structured logging configuration with automatic secret masking."""

from __future__ import annotations

import logging
import re
from typing import List, Optional

# Secret patterns to automatically mask in log output
SECRET_PATTERNS: List[re.Pattern] = [
    re.compile(r"AIza[0-9A-Za-z\-_]{20,}", re.IGNORECASE),
    re.compile(r"tvly-[0-9A-Za-z\-_]{10,}", re.IGNORECASE),
    re.compile(r"(api[_\-\s]?key\s*[:=]\s*)['\"]?([A-Za-z0-9_\-]{8,})['\"]?", re.IGNORECASE),
    re.compile(r"bearer\s+[A-Za-z0-9\._~\+\/\-]+=*", re.IGNORECASE),
]


class SecretMaskingFilter(logging.Filter):
    """Logging filter that scrubs credential patterns from log messages and arguments."""

    def filter(self, record: logging.LogRecord) -> bool:
        if record.msg and isinstance(record.msg, str):
            record.msg = self.mask_text(record.msg)

        if record.args:
            if isinstance(record.args, dict):
                record.args = {k: self.mask_item(v) for k, v in record.args.items()}
            elif isinstance(record.args, tuple):
                record.args = tuple(self.mask_item(v) for v in record.args)
            elif isinstance(record.args, list):
                record.args = [self.mask_item(v) for v in record.args]

        return True

    @classmethod
    def mask_text(cls, text: str) -> str:
        """Replace sensitive patterns with [REDACTED_SECRET]."""
        sanitized = text
        for pattern in SECRET_PATTERNS:
            sanitized = pattern.sub("[REDACTED_SECRET]", sanitized)
        return sanitized

    @classmethod
    def mask_item(cls, item: object) -> object:
        if isinstance(item, str):
            return cls.mask_text(item)
        return item


def configure_logging(level: str = "INFO", log_format: Optional[str] = None) -> None:
    """Configure root application logger with secret masking enabled."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    fmt = log_format or "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s"

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(fmt))
    handler.addFilter(SecretMaskingFilter())

    root = logging.getLogger()
    root.setLevel(numeric_level)

    # Avoid duplicate handlers on re-configuration
    root.handlers.clear()
    root.addHandler(handler)
