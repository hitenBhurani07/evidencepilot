# Requirements and Acceptance Criteria

This living document maps every requirement from the assignment brief, charter, and engineering specifications to observable code, test, and demonstration evidence.

## Traceability Matrix

| ID | Requirement | Type | Target Layer / Component | Verification Evidence & Acceptance Check | Status |
|---|---|---|---|---|---|
| R01 | Accept user research question via CLI, API, or UI | EXPLICIT | `evidencepilot.schemas` / `evidencepilot.agent` | Unit tests for input validation (empty question, length bounds, sanitization) | PENDING |
| R02 | Generate an explicit, visible research plan before execution | EXPLICIT | `evidencepilot.agent.planner` | Schema test validating typed Plan object (steps, search queries, target URLs) | PENDING |
| R03 | Select and execute at least two distinct tools in the research workflow | EXPLICIT | `evidencepilot.tools.search`, `evidencepilot.tools.extractor` | Mock and live execution showing both web search and URL content extraction in the live execution path | PENDING |
| R04 | Retrieve, clean, normalize, and filter source evidence | EXPLICIT | `evidencepilot.tools.source_scorer` | Unit tests for URL canonicalization, deduplication, content-length filtering, domain scoring | PENDING |
| R05 | Synthesize structured answer using only verified evidence | EXPLICIT | `evidencepilot.agent.synthesizer` | Pydantic validation tests, refusal/low-evidence tests, prompt injection isolation | PENDING |
| R06 | Final output includes: question, short answer, key findings, citations, confidence score/rationale, assumptions, limitations, and next steps | EXPLICIT | `evidencepilot.schemas.research` | Schema compliance test ensuring all required fields are present and typed | PENDING |
| R07 | Robust failure handling for network timeouts, 429 rate limits, empty results, and malformed provider responses | EXPLICIT | `evidencepilot.providers`, `evidencepilot.tools` | Unit tests for timeout, retry backoff limits, fallback to low-evidence summary | PENDING |
| R08 | Prompt injection awareness & defense | EXPLICIT | `evidencepilot.tools.extractor`, `evidencepilot.agent.synthesizer` | Fixture test where untrusted web content contains prompt injection payload ("ignore instructions"); agent treats as data, not instruction | PENDING |
| R09 | Tracing, structured logging, latency & cost metrics | EXPLICIT | `evidencepilot.logging` | Execution metadata logs query latency, source counts, token usage, without leaking secrets | PENDING |
| R10 | Evaluation suite with at least 5 distinct queries across categories | EXPLICIT | `docs/TEST_PLAN_AND_EVALUATION.md`, `tests/test_evaluation.py` | Recorded execution of 5+ test queries with expected vs observed behavior | PENDING |
| R11 | Comprehensive README covering setup, architecture, decisions, limitations, and future improvements | EXPLICIT | `README.md` | Clean-environment verification from documented setup instructions | PENDING |
| R12 | 3–5 minute video demonstration runbook showing happy path and edge/failure case | EXPLICIT | `docs/DEMO_RUNBOOK.md` | Video recording script and verified runbook | PENDING |
| R13 | 2–3 sample output reports stored as artifacts | EXPLICIT | `artifacts/*.json`, `artifacts/*.md` | Real run outputs formatted and preserved in `artifacts/` | PENDING |
| R14 | AI tool usage disclosure | EXPLICIT | `docs/AI_USAGE_DISCLOSURE.md` | Detailed attribution of AI tools used during development | PENDING |
| R15 | Zero secret leakage in repository, logs, or error outputs | ENGINEERING DECISION | `evidencepilot.config` | Redaction tests, `.gitignore` validation, pre-commit/status scans | PASS (Stage 01) |
| R16 | Safe URL extraction (timeouts, byte limits, private IP/loopback blocking) | ENGINEERING DECISION | `evidencepilot.tools.extractor` | URL policy tests blocking `localhost`, `127.0.0.1`, `10.0.0.0/8`, `169.254.169.254` | PENDING |
| R17 | Strict Free-Tier cost guardrail (Gemini free tier + Tavily free tier) | ENGINEERING DECISION | `evidencepilot.providers` | Verification of free models and zero billing requirements | PENDING |
| R18 | No remote database / Firebase overhead by default; local artifacts only | ENGINEERING DECISION | `evidencepilot.storage` | Decision log D-005 rationale; local JSON/Markdown run storage | PASS (Stage 01) |
| R19 | Thin Streamlit UI for interactive demonstration | OPTIONAL | `src/evidencepilot/ui/app.py` | Streamlit interactive app running locally if dependencies allow | PENDING |

## Acceptance Gate Protocol
- A requirement is marked `PASS` only after actual test verification and observable logs.
- `PENDING` means scheduled for an upcoming implementation stage.
- `BLOCKED` means waiting for a human handoff or external resource.
- No fixture or mock shall be misrepresented as a live API test.
