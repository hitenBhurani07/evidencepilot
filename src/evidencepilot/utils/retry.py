"""Safe retry utility with bounded attempts and exponential backoff."""

from __future__ import annotations

import logging
import random
import time
from typing import Any, Callable, Sequence, Tuple, Type, TypeVar

from evidencepilot.providers.base import AuthError, ContentFilterError

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Non-retryable error types (retrying will never fix an auth or content violation)
NON_RETRYABLE_EXCEPTIONS: Tuple[Type[Exception], ...] = (
    AuthError,
    ContentFilterError,
)


def retry_with_backoff(
    func: Callable[[], T],
    max_attempts: int = 3,
    initial_delay: float = 0.5,
    max_delay: float = 4.0,
    backoff_factor: float = 2.0,
    retryable_exceptions: Sequence[Type[Exception]] = (Exception,),
) -> T:
    """Execute a function with bounded retries and jittered exponential backoff.
    
    Immediately aborts and re-raises on authentication or content policy errors.
    """
    attempt = 0
    delay = initial_delay

    while True:
        attempt += 1
        try:
            return func()
        except NON_RETRYABLE_EXCEPTIONS:
            # Fatal error; never retry
            raise
        except Exception as exc:
            if not any(isinstance(exc, exc_cls) for exc_cls in retryable_exceptions):
                raise

            if attempt >= max_attempts:
                logger.warning(
                    "Exceeded maximum retry attempts (%d/%d). Last failure: %s",
                    attempt,
                    max_attempts,
                    exc,
                )
                raise

            # Add jitter to delay (+/- 20%)
            jitter = delay * random.uniform(0.8, 1.2)
            logger.info(
                "Retry attempt %d/%d after %.2fs backoff due to transient failure: %s",
                attempt,
                max_attempts,
                jitter,
                exc,
            )
            time.sleep(jitter)
            delay = min(delay * backoff_factor, max_delay)
