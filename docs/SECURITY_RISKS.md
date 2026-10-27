# EvidencePilot — Security Risks and Mitigations

**Status:** Living document updated at Stage 06.  
**Scope:** Research-assistant assignment prototype, not a production service.

---

## Mitigations implemented in this release

| Risk | Mitigation | Location |
|---|---|---|
| **SSRF via URL fetch** | Reject non-HTTP(S) schemes; block localhost, link-local, private, multicast, and cloud-metadata IPs (127.0.0.0/8, 169.254.0.0/16, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16); DNS-resolution check on each redirect target | `tools/url_policy.py`, `tools/extractor.py` |
| **Credential leakage in logs** | `SecretMaskingFilter` auto-redacts Gemini key patterns (`AIza…`), Tavily key patterns (`tvly-…`), bearer tokens, and generic `api_key=…` strings from every log record | `logging.py` |
| **Credential leakage in config display** | `mask_secret()` shows only key length + first 4 / last 2 characters | `config.py` |
| **Prompt injection via fetched page content** | All untrusted evidence text is wrapped in `<evidence>…</evidence>` XML-style boundaries with an `UNTRUSTED DATA BOUNDARY` annotation in the system instruction before being passed to the LLM | `agent/synthesizer.py` |
| **Unbounded API spend** | Per-run limits: `max_search_queries ≤ 10`, `max_fetch_pages ≤ 15`, `request_timeout_seconds ≤ 60`; per-request limits also enforced in `ResearchRequest` | `config.py`, `schemas/research.py`, `agent/orchestrator.py` |
| **Excessive retries** | `retry_with_backoff` caps at `max_attempts=3` with jittered exponential backoff; auth errors never retried | `utils/retry.py` |
| **Non-retryable auth errors** | `AuthError` and `ContentFilterError` bypass retry loop immediately | `utils/retry.py`, `providers/base.py` |
| **Raw exception text leaking keys** | `GeminiProvider._map_exception` redacts the raw API key before forwarding error messages; exceptions are caught and classified before propagation | `providers/gemini.py` |
| **Shell or file injection via page content** | Agent uses no shell execution or `eval()`; all tool calls go through typed Pydantic schemas with strict field validation; page content is treated as plain text only | Architecture |
| **Redirect chaining to private hosts** | Manual redirect loop re-validates every redirect target through `validate_target_url` before following | `tools/extractor.py` |
| **Excessive page sizes** | HTTP body limited to 512 KB; truncated at 6 000 characters of extracted text | `tools/extractor.py` |

---

## Risks that are **not** fully solved in this prototype

The following risks exist and are documented honestly.  
They are acceptable scope limitations for a course assignment:

### 1. DNS rebinding
After validation, a DNS entry could be updated to point to a private IP before the actual TCP connection is opened.  
**Impact:** Low in practice for short-lived research tasks.  
**Would need:** Connection-level IP verification inside the TCP stack or a proxy with IP pinning.

### 2. Time-of-check / Time-of-use (TOCTOU) on redirects
There is a brief window between redirect-target DNS validation and the next HTTP request where DNS could change.  
**Impact:** Very low for a synchronous research run.  
**Would need:** Same IP pinning as above.

### 3. LLM prompt injection — completeness
Wrapping evidence in XML boundaries makes injection harder, but a sufficiently crafted payload might still influence LLM behaviour.  
**Impact:** Medium risk — a malicious web page could attempt to alter the generated answer or insert false citations.  
**Would need:** A red-team evaluation, output-side safety classifier, and human-in-the-loop review for high-stakes use.

### 4. Rate limiting is per-run, not cross-session
The current budget (`max_search_queries`, `max_fetch_pages`) is enforced within a single research run. A caller could launch many concurrent runs.  
**Impact:** API cost overrun if deployed as a service.  
**Would need:** A persistent request counter, user quota enforcement, and API gateway rate limits.

### 5. .env file confidentiality
The `.env` file (with live API keys) is excluded from git by `.gitignore` but remains in plaintext on disk.  
**Impact:** Local machine compromise exposes all credentials.  
**Would need:** OS-level secret manager (e.g. Windows Credential Manager, macOS Keychain, or cloud secret manager) for a real deployment.

### 6. Fetched page trust level
All fetched pages are treated as equally untrusted regardless of domain. There is no TLS certificate pinning or domain allowlist.  
**Impact:** A CDN compromise could serve malicious content.  
**Would need:** Explicit domain allowlist or certificate transparency checks for production use.

### 7. No output sanitization for HTML/markdown rendering
`StructuredAnswer` fields are plain text. If rendered as HTML in a UI without escaping, XSS could occur.  
**Impact:** Relevant only if a web UI is added.  
**Would need:** HTML escaping in the UI layer (already planned for Stage 08 Streamlit demo).

---

## Audit trail

- Stage 06 review date: 2026-10-27
- Reviewer: Antigravity agent (automated) + human project owner
- Secret-scan method: `SecretMaskingFilter` unit tests; `.gitignore` check via `git check-ignore`
- No secrets were found in committed code as of this review.

---

*This document is intentionally honest about limitations. The prototype does not claim production-grade security.*
