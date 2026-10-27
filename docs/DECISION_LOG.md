# Decision Log

> Add decisions when made. Do not fabricate past debugging events or dates. Each entry should explain context, alternatives, why chosen, tradeoffs, and evidence.

## D-001 — Custom single-agent orchestration
- **Status:** Approved (Active).
- **Context:** Assignment needs a visible plan, tool selection, source-grounded synthesis, failure handling, evaluation.
- **Options:** Custom planner; agent framework (LangChain/CrewAI); multi-agent architecture.
- **Choice:** Small custom planner/orchestrator.
- **Why:** Low complexity, explicit flow, straightforward testing, aligns with assignment guidance.
- **Tradeoff:** Some tool routing/retry logic must be written manually.

## D-002 — Python + Pydantic + Pytest
- **Status:** Approved (Active).
- **Why:** Clear contracts, validation, convenient testing, aligns with user skills.
- **Tradeoff:** Dependency versions must be documented and tested.

## D-003 — Gemini free tier as the LLM provider
- **Status:** Approved (Active, Offline verified with fakes).
- **Why:** Official `google-genai` SDK with `gemini-2.5-flash` model which provides generous free-tier quotas under Google AI Studio without credit card billing.
- **Guardrails:** Select only a model shown as free for the project; use official current SDK/docs; do not enable billing or upgrade tier; record rate limits/data-use caveat.
- **Tradeoff:** Quota/model access can vary, and Google documentation notes free-tier prompt data may be used to improve Google products. Sensitive company data should not be processed.

## D-004 — Tavily free tier as default search provider
- **Status:** Approved (Active, Offline verified with fakes).
- **Why:** Official quickstart currently documents 1,000 free credits/month and no credit card requirement; purpose-built for AI agents with clean snippet and text extraction.
- **Alternatives:** Brave Search API (requires credit card/plan activation for monthly free credits), SerpApi (requires credit card for high volume), scraping Google/DuckDuckGo (unreliable, brittle, violates terms).
- **Tradeoff:** 1,000 requests/month cap. Research agent must bound searches per query (default 3) to preserve quota.

## D-005 — No Firebase/database initially
- **Status:** Approved (Active).
- **Why:** Assignment does not require user accounts or persistent multi-user state; local artifacts/logs suffice.
- **Alternative:** SQLite if local persistence materially helps; Firebase only after an approved requirement.
- **Tradeoff:** No cross-device persistence or hosted run history.

## D-006 — Real tools and test doubles separated
- **Status:** Approved (Active).
- **Why:** Deterministic offline testing is useful without credentials, but live user-facing flow must be honest.
- **Tradeoff:** Requires clearly labelling live versus mock results.

## D-007 — Narrow provider protocols and localized Pydantic validation
- **Status:** Approved (Stage 02).
- **Context:** LLM and search APIs can change response formats, fail unexpectedly, or return malformed JSON.
- **Choice:** Define strict `LLMProvider` and `SearchProvider` protocols in `base.py`. Enforce client-side Pydantic validation on parsed responses and map errors into sanitized domain exceptions (`AuthError`, `RateLimitError`, `NetworkError`, `SchemaValidationError`).
- **Consequences:** Eliminates secret leaks in stack traces, guarantees schema compliance before synthesis reaches the user, and enables seamless switching between deterministic test doubles and live providers.
