# Risk Register

| Risk | Likelihood/impact | Mitigation | Evidence to collect |
|---|---|---|---|
| Free-tier quota exhausted or model unavailable | Medium / Medium | Select free-tier model, budget calls, one smoke test, retries capped | Config, smoke-test status, rate-limit behavior |
| Provider terms/pricing change | Medium / Medium | Recheck official pricing before live setup; never enable billing automatically | Setup date and links |
| API key leaks in Git/log/UI | Low / High | `.env` ignored, redacted errors, secret scan, no chat sharing | Git status and safe scan result |
| Webpage prompt injection | Medium / High | Treat retrieved text as untrusted evidence; fixture test | Security test results |
| Unsafe URL/SSRF | Medium / High | Scheme/domain/IP checks, redirect checks, size/time limits | URL policy test results |
| Weak/stale/SEO-optimized sources | High / Medium | dedupe, source metadata, conflict reporting, source-quality notes | evaluation examples |
| Hallucinated findings/citations | Medium / High | only use retrieved evidence; validate source IDs; low-evidence fallback | answer validator tests |
| Rate-limits/network failures | Medium / Medium | bounded retry/backoff, partial failure fallback | integration-mock test results |
| Student cannot explain AI-generated implementation | Medium / High | living journal, architecture walkthrough, code explanations and mock interview | user-review checklist |
| Overengineering wastes deadline | Medium / High | prioritize explicit requirements; no Firebase/deployment/multi-agent by default | acceptance matrix |
| Demo/repo links inaccessible | Medium / High | final external access checks and manual handoff | verified URLs/permissions |
