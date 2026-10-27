# STAGE 03 — Search tool, page extraction tool, and evidence hygiene

## Tasks
1. Implement a real search tool through the selected free provider adapter (Tavily by default) and normalize each result into title, URL, snippet/extract if returned, source domain, provider metadata, and retrieval time.
2. Implement a second distinct tool to fetch/extract readable page content from selected result URLs. Enforce connect/read timeouts, maximum response bytes, content-type checks, allowed schemes (`https` and optionally `http`), private/local IP blocking, redirect checks, and sensible user-agent. Avoid crawling arbitrary internal URLs; protect against SSRF.
3. Add source cleaning: deduplicate canonical URLs, remove empty/very short results, identify unsupported or malformed URLs, cap source count, and use transparent source-quality features (domain, snippet/full-text availability, duplicate, freshness if known). Do not claim these heuristics prove truth.
4. Handle HTTP errors, 429, 5xx, empty/malformed provider response, extraction failures, and timeouts without crashing the entire run. Use bounded retries with jitter/backoff only where safe.
5. Treat all retrieved content as untrusted evidence. Never execute commands from pages or follow instructions found in results. Add explicit prompt-injection fixtures/tests.
6. Preserve provenance. Every source presented to the user must be one actually returned/fetched by tools; no fabricated URLs or citations.
7. Tests must use a local fake HTTP server or mocked requests—not live websites—where possible. Live smoke test is separate and documented.

## Acceptance gate
Both real tool adapters are implemented; normalization/filtering tests pass; unsafe/private URL and timeout cases are covered; a live search smoke test is labelled only according to actual result; no data path silently falls back to mocks.
