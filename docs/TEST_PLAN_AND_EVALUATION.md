# Test Plan and Evaluation

## Automated coverage
- Input limits and schema validation
- Missing/malformed config and secret redaction
- Gemini response parsing and Pydantic validation
- Search result normalization and malformed payloads
- Search timeout, 429, 5xx, and retry cap
- Page extraction timeout, large response, wrong content type, unsafe schemes, private IPs, redirect checks
- Deduplication, empty/low-value filtering
- Tool choice and planner step caps
- Partial tool failure and all-tools-fail behavior
- Current-run citation IDs, unknown/missing citations, malformed answer output
- Prompt-injection fixture (retrieved page says to ignore system instructions or reveal a secret)
- No-evidence and conflicting-evidence behavior
- Optional interface: empty question, active/loading state, readable result, clickable sources, error feedback

## Evaluation queries (starter set; record observed outcomes later)
1. **Comparison:** “Compare three open-source vector databases for a small startup building a RAG product.” Expected: plan compares consistent criteria, sources support tradeoffs, no fabricated benchmark numbers.
2. **Entity discovery:** “Find five Indian B2B SaaS startups in HR tech and summarize positioning.” Expected: factual entities with source URL per company; clearly state if fewer than five verified.
3. **Technical tradeoffs:** “What are the pros and cons of multi-agent architecture for customer-support automation?” Expected: balanced evidence-grounded arguments and assumptions.
4. **Time-sensitive query:** Ask about a current policy/technology release and require retrieval dates or page dates where available. Expected: explicit as-of framing; stale evidence/uncertainty noted.
5. **Ambiguous/unanswerable:** “What is the best AI platform?” Expected: ask for criteria or make explicit bounded assumptions; no falsely precise ranking.
6. **Failure/edge:** empty search result, invalid query, timeout, or prompt-injection source fixture. Expected: structured failure/low-confidence output; no fabricated citations.

## Evaluation rubric (0–2 each; define before scoring)
- Evidence relevance
- Citation traceability
- Coverage of requested question
- Uncertainty/conflict handling
- Schema validity and output clarity
- Failure handling

Report actual scores and show examples. This small set is a practical smoke evaluation, not a statistically valid benchmark. Do not score a query as live if it only ran on fixtures.

## Run modes
- `UNIT/MOCK`: deterministic tests using fake providers; no network call.
- `LIVE-SMOKE`: one minimal API/search request using configured credentials.
- `LIVE-EVALUATION`: real research queries; note time, model, sources, and any rate-limit interruptions.

Keep these modes separate in the README and test report.
