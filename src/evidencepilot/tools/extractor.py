"""Web page content fetcher and reader with SSRF guards and size limits."""

from __future__ import annotations

import logging
import re
from typing import Optional, Set
from bs4 import BeautifulSoup
import httpx
from pydantic import BaseModel, Field

from evidencepilot.tools.url_policy import UnsafeURLError, validate_target_url

logger = logging.getLogger(__name__)

ALLOWED_CONTENT_TYPES: Set[str] = {
    "text/html",
    "text/plain",
    "application/xhtml+xml",
}


class ExtractionResult(BaseModel):
    """Result of fetching and extracting text from a web page."""
    
    url: str
    status_code: Optional[int] = None
    title: Optional[str] = None
    content: str = ""
    is_success: bool = False
    error_message: Optional[str] = None
    byte_count: int = 0


class PageExtractor:
    """Safe HTTP client and text extractor for research pages."""
    
    DEFAULT_USER_AGENT = "EvidencePilot-ResearchAgent/0.1 (+https://github.com/evidencepilot/agent)"
    
    def __init__(
        self,
        timeout_seconds: float = 10.0,
        max_bytes: int = 512 * 1024,  # 512 KB
        max_text_chars: int = 6000,
        max_redirects: int = 3,
        user_agent: Optional[str] = None,
    ):
        self.timeout_seconds = timeout_seconds
        self.max_bytes = max_bytes
        self.max_text_chars = max_text_chars
        self.max_redirects = max_redirects
        self.user_agent = user_agent or self.DEFAULT_USER_AGENT

    def extract(self, url: str) -> ExtractionResult:
        """Fetch URL and extract readable text, enforcing SSRF and size bounds."""
        current_url = url.strip()
        
        # 1. Validate initial URL
        try:
            current_url = validate_target_url(current_url)
        except UnsafeURLError as unsafe_err:
            logger.warning("Blocked unsafe URL request: %s - %s", url, unsafe_err)
            return ExtractionResult(
                url=url,
                is_success=False,
                error_message=f"Security policy blocked URL: {unsafe_err}",
            )

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,text/plain;q=0.9,*/*;q=0.1",
            "Accept-Language": "en-US,en;q=0.8",
        }

        # 2. Execute fetch with manual redirect loop to validate redirect targets
        redirects_followed = 0
        try:
            with httpx.Client(timeout=self.timeout_seconds, follow_redirects=False) as client:
                while True:
                    req = client.build_request("GET", current_url, headers=headers)
                    resp = client.send(req, stream=True)

                    if resp.is_redirect:
                        redirects_followed += 1
                        if redirects_followed > self.max_redirects:
                            resp.close()
                            return ExtractionResult(
                                url=url,
                                status_code=resp.status_code,
                                is_success=False,
                                error_message=f"Exceeded max redirects ({self.max_redirects})",
                            )

                        redirect_target = resp.headers.get("location")
                        resp.close()
                        if not redirect_target:
                            return ExtractionResult(
                                url=url,
                                is_success=False,
                                error_message="Redirect header missing location",
                            )

                        # Resolve relative redirect URLs against current URL
                        from urllib.parse import urljoin
                        next_url = urljoin(current_url, redirect_target)
                        
                        # Validate next URL against SSRF policy
                        try:
                            current_url = validate_target_url(next_url)
                        except UnsafeURLError as redirect_err:
                            return ExtractionResult(
                                url=url,
                                is_success=False,
                                error_message=f"Redirect to unsafe URL blocked: {redirect_err}",
                            )
                        continue

                    # Non-redirect response reached
                    break

                # 3. Check status code
                if resp.status_code != 200:
                    status = resp.status_code
                    resp.close()
                    return ExtractionResult(
                        url=current_url,
                        status_code=status,
                        is_success=False,
                        error_message=f"HTTP server returned status {status}",
                    )

                # 4. Check Content-Type
                content_type = resp.headers.get("content-type", "").lower()
                main_type = content_type.split(";")[0].strip()
                if main_type and main_type not in ALLOWED_CONTENT_TYPES:
                    resp.close()
                    return ExtractionResult(
                        url=current_url,
                        status_code=200,
                        is_success=False,
                        error_message=f"Unsupported Content-Type '{main_type}'. Expected text/html or text/plain.",
                    )

                # 5. Read body with byte bounds check
                content_bytes = bytearray()
                for chunk in resp.iter_bytes(chunk_size=8192):
                    content_bytes.extend(chunk)
                    if len(content_bytes) > self.max_bytes:
                        resp.close()
                        return ExtractionResult(
                            url=current_url,
                            status_code=200,
                            byte_count=len(content_bytes),
                            is_success=False,
                            error_message=f"Content exceeded size limit of {self.max_bytes} bytes",
                        )
                resp.close()

        except httpx.TimeoutException:
            return ExtractionResult(
                url=current_url,
                is_success=False,
                error_message=f"Request timed out after {self.timeout_seconds}s",
            )
        except httpx.RequestError as req_err:
            return ExtractionResult(
                url=current_url,
                is_success=False,
                error_message=f"Network error: {req_err}",
            )
        except Exception as exc:
            return ExtractionResult(
                url=current_url,
                is_success=False,
                error_message=f"Extraction failure: {exc}",
            )

        # 6. Parse and clean HTML text
        raw_text = content_bytes.decode("utf-8", errors="replace")
        title, clean_content = self._parse_html(raw_text)

        # Truncate clean content to bounds
        if len(clean_content) > self.max_text_chars:
            clean_content = clean_content[:self.max_text_chars] + "\n...[truncated]"

        return ExtractionResult(
            url=current_url,
            status_code=200,
            title=title,
            content=clean_content,
            is_success=True,
            byte_count=len(content_bytes),
        )

    def _parse_html(self, raw_html: str) -> tuple[Optional[str], str]:
        """Strip non-content elements and extract clean textual narrative."""
        soup = BeautifulSoup(raw_html, "html.parser")

        # Extract title
        title: Optional[str] = None
        if soup.title and soup.title.string:
            title = soup.title.string.strip()

        # Remove noisy structural elements
        for tag in soup.find_all(["script", "style", "nav", "header", "footer", "noscript", "svg", "form", "aside"]):
            tag.decompose()

        # Extract remaining text
        text = soup.get_text(separator="\n")
        # Collapse excessive newlines and spaces
        lines = [line.strip() for line in text.splitlines()]
        clean_text = "\n".join(line for line in lines if line)
        clean_text = re.sub(r"\n{3,}", "\n\n", clean_text)
        return title, clean_text
