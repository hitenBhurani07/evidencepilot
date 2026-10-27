# Risk Register — EvidencePilot

This risk register documents architectural, operational, and security risks identified, their active mitigations, and honest residual risks that remain outside the scope of a lightweight take-home assignment.

## Risk Assessment Matrix

| ID | Risk Description | Severity | Likelihood | Active Implementation Mitigation | Residual Risk & Unresolved Boundaries |
|---|---|---|---|---|---|
| RSK-01 | **API Secret Leakage** via git commits, error messages, or shell logs | HIGH | LOW | `.env` ignored in `.gitignore`, `SecretMaskingFilter` scrub on all logs, client-side redaction in `mask_secret` | If user explicitly prints `os.environ` outside the application, keys could be exposed to stdout. |
| RSK-02 | **SSRF / Internal Infrastructure Scanning** via malicious redirect or URL input | HIGH | LOW | `validate_target_url` blocks private/loopback/link-local IPs (`127.0.0.1`, `10.0.0.0/8`, `169.254.169.254`); manual redirect verification re-checks target IPs | DNS rebinding attacks where hostname changes IP between check and connect cannot be 100% prevented without kernel-level socket pinning or isolated egress proxies. |
| RSK-03 | **Indirect Prompt Injection** from adversarial web pages | HIGH | MEDIUM | HTML parsed and stripped of `<script>`, `<style>`, `<form>`; evidence wrapped in strict `<evidence>` delimiters; system prompt directs model to treat content as passive data | Sophisticated adversarial linguistic jailbreaks in text content may still bias model tone or induce minor hallucinations in edge cases. |
| RSK-04 | **Citation Hallucination / Phantom Sources** | HIGH | MEDIUM | Set intersection validation in `ResearchSynthesizer._validate_and_sanitize_citations()`; invalid IDs are stripped and confidence penalized | Model may cite a valid source ID `[S1]` for a statement only partially implied by Source S1. |
| RSK-05 | **Resource Exhaustion (ReDoS, Decompression Bombs, Giant Files)** | MEDIUM | LOW | Streaming chunk reads with strict 512 KB cap (`max_bytes`), request timeout (10s), text truncation (6,000 chars) | Malformed binary responses claiming to be `text/html` may cause minor UTF-8 decoding overhead. |
| RSK-06 | **Free-Tier Rate Limits (HTTP 429) & Quota Exhaustion** | MEDIUM | HIGH | Jittered exponential backoff with 3-attempt ceiling; immediate abort on 401/403; strict query budgets (max 3 searches, max 4 fetches) | During peak hours, Google AI Studio or Tavily free tier may throttle requests consecutively, causing zero-evidence fallback. |
| RSK-07 | **Third-Party Data Privacy on Free Tier** | MEDIUM | MEDIUM | Clear disclosure in documentation and README that Google AI Studio free-tier prompts may be reviewed by human trainers to improve products | Production compliance (HIPAA/GDPR) requires enterprise paid tiers with zero data-retention guarantees. |
| RSK-08 | **Stale or Contradictory Online Information** | MEDIUM | HIGH | Transparent heuristic scoring favoring authoritative TLDs (.edu, .gov); conflict reporting in `limitations` and `assumptions` | Heuristics do not constitute epistemic truth verification; SEO-manipulated articles can score moderately well. |

## Production Scaling Limitations & Tradeoffs
1. **No Sandboxed Browser Execution:** EvidencePilot uses lightweight HTTP requests (`httpx` + `BeautifulSoup`). Single Page Applications (SPAs) relying purely on client-side React/Vue rendering cannot be executed without headless Chromium (Playwright/Puppeteer), which was intentionally excluded to avoid heavy binary dependencies.
2. **In-Memory Event Bus:** Observability is in-process. For production distributed scale, events should stream to OpenTelemetry / Kafka / Cloud Trace.
3. **Local Artifact Storage:** Runs are stored locally as JSON and Markdown files. Multi-tenant storage would require PostgreSQL or Cloud Storage.
