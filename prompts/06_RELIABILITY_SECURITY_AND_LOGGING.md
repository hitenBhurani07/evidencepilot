# STAGE 06 — Reliability, security, observability, and cost guardrails

## Tasks
1. Review all external calls for timeouts, capped retries, error categories, empty/malformed output handling, and deterministic fallback behavior.
2. Ensure keys are never logged or shown. Verify `.env` and artifact files containing secrets are ignored. Add a secret-pattern scan to the final audit where tools are available.
3. Add SSRF protections to URL fetch tool: reject localhost, private, link-local, and reserved addresses; verify DNS resolution/redirects safely; reject `file:`, `ftp:`, and other schemes. Document limits and test.
4. Add prompt-injection tests and ensure page content cannot cause shell/file actions, policy override, key disclosure, or extra tool permissions.
5. Add bounded request budgets: maximum searches per query, maximum pages, max page bytes, max output tokens, overall timeout, and max retries. Keep defaults modest to preserve free API quota.
6. Add structured logging with run id, timing, stage, counts, and error category only. Avoid query logging by default if it could contain private material; allow redaction/config where sensible.
7. Add health/config checks and readable error messages for common API errors (missing key, invalid key, rate limit, model unavailable, timeout).
8. Document risks that cannot be fully solved in a small assignment. Do not claim comprehensive production security.

## Acceptance gate
Reliability/security tests pass offline; logs do not leak secrets; cost/latency guardrails are configured and documented; remaining risks are recorded accurately.
