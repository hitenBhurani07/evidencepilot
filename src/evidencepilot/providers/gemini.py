"""Gemini API provider adapter using the official google-genai SDK."""

from __future__ import annotations

import json
from typing import Any, Optional, Type, TypeVar
from pydantic import BaseModel, ValidationError

from evidencepilot.providers.base import (
    AuthError,
    ContentFilterError,
    NetworkError,
    ProviderError,
    RateLimitError,
    SchemaValidationError,
)

T = TypeVar("T", bound=BaseModel)


class GeminiProvider:
    """Production wrapper for Google Gemini API."""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        if not api_key or not api_key.strip():
            raise AuthError("API key cannot be empty", provider_name="gemini")
        self.api_key = api_key.strip()
        self.model_name = model_name
        self._client: Optional[Any] = None

    def _get_client(self) -> Any:
        """Lazily initialize Google GenAI Client."""
        if self._client is None:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except ImportError as err:
                raise ProviderError(
                    "google-genai SDK is not installed. Run 'pip install google-genai'.",
                    provider_name="gemini"
                ) from err
            except Exception as exc:
                raise self._map_exception(exc)
        return self._client

    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Generate unstructured text with temperature control."""
        client = self._get_client()
        try:
            from google.genai import types
            
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2,
            )
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config,
            )
            if not response.text:
                raise ProviderError("Empty response text returned from Gemini", provider_name="gemini")
            return response.text
        except Exception as exc:
            raise self._map_exception(exc)

    def generate_structured(
        self,
        prompt: str,
        schema_class: Type[T],
        system_instruction: Optional[str] = None,
    ) -> T:
        """Generate structured JSON adhering to a Pydantic schema and validate locally."""
        client = self._get_client()
        try:
            from google.genai import types
            
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=schema_class,
                temperature=0.1,
            )
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config,
            )
            raw_text = response.text
            if not raw_text:
                raise ProviderError("Empty structured response returned from Gemini", provider_name="gemini")
            
            return self._parse_and_validate(raw_text, schema_class)
        except Exception as exc:
            raise self._map_exception(exc)

    def _parse_and_validate(self, raw_text: str, schema_class: Type[T]) -> T:
        """Parse JSON and validate against the Pydantic schema with sanitized error handling."""
        cleaned = raw_text.strip()
        # Handle markdown JSON fence if present
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            parsed_dict = json.loads(cleaned)
        except json.JSONDecodeError as json_err:
            raise SchemaValidationError(
                f"Failed to parse JSON response from Gemini: {json_err}",
                provider_name="gemini"
            ) from json_err

        try:
            return schema_class.model_validate(parsed_dict)
        except ValidationError as val_err:
            raise SchemaValidationError(
                f"Response failed Pydantic schema validation for {schema_class.__name__}: {val_err.error_count()} errors found",
                provider_name="gemini"
            ) from val_err

    def _map_exception(self, exc: Exception) -> Exception:
        """Map raw provider errors into sanitized domain exceptions without leaking credentials."""
        if isinstance(exc, ProviderError):
            return exc
            
        err_msg = str(exc)
        # Redact API key if it inadvertently appears in raw error text
        if self.api_key and self.api_key in err_msg:
            err_msg = err_msg.replace(self.api_key, "[REDACTED_API_KEY]")

        err_lower = err_msg.lower()
        if "401" in err_lower or "403" in err_lower or "api_key" in err_lower or "permission_denied" in err_lower:
            return AuthError(f"Authentication failed: {err_msg}", provider_name="gemini", status_code=401)
        if "429" in err_lower or "quota" in err_lower or "resource_exhausted" in err_lower or "rate limit" in err_lower:
            return RateLimitError(f"Quota or rate limit exceeded: {err_msg}", provider_name="gemini", status_code=429)
        if "timeout" in err_lower or "connection" in err_lower or "network" in err_lower:
            return NetworkError(f"Network error during call: {err_msg}", provider_name="gemini")
        if "safety" in err_lower or "blocked" in err_lower or "harm" in err_lower:
            return ContentFilterError(f"Content blocked by safety policy: {err_msg}", provider_name="gemini")

        return ProviderError(f"Unexpected provider error: {err_msg}", provider_name="gemini")
