# Decision Log

> Add decisions when made. Do not fabricate past debugging events or dates. Each entry should explain context, alternatives, why chosen, tradeoffs, and evidence.

## D-001 — Custom single-agent orchestration
- **Status:** Planned default; confirm during implementation.
- **Context:** Assignment needs a visible plan, tool selection, source-grounded synthesis, failure handling, evaluation.
- **Options:** Custom planner; agent framework; multi-agent architecture.
- **Choice:** Small custom planner/orchestrator.
- **Why:** Low complexity, explicit flow, straightforward testing, aligns with assignment guidance.
- **Tradeoff:** Some tool routing/retry logic must be written manually.

## D-002 — Python + Pydantic + Pytest
- **Status:** Planned default.
- **Why:** Clear contracts, validation, convenient testing, aligns with user skills.
- **Tradeoff:** Dependency versions must be documented and tested.

## D-003 — Gemini free tier as the LLM provider
- **Status:** User-reported key availability; live access not yet verified.
- **Why:** User has a key and requested free options.
- **Guardrails:** Select only a model shown as free for the project; use official current SDK/docs; do not enable billing or upgrade tier; record rate limits/data-use caveat.
- **Tradeoff:** quota/model access can vary, and free-tier data may be used to improve provider products.

## D-004 — Tavily free tier as default search provider
- **Status:** Recommended default pending actual account verification.
- **Why:** Official quickstart currently documents 1,000 free credits/month and no credit card; purpose-built for agent search.
- **Alternatives:** Existing user search API (if already configured and named); Brave Search API (currently provides monthly credits but may require plan activation/payment setup); unofficial scraping (not selected due to reliability/terms concerns).
- **Tradeoff:** API quota and terms can change; monitor usage and keep provider abstracted.

## D-005 — No Firebase/database initially
- **Status:** Planned default.
- **Why:** Assignment does not require user accounts or persistent multi-user state; local artifacts/logs suffice.
- **Alternative:** SQLite if local persistence materially helps; Firebase only after an approved requirement.
- **Tradeoff:** No cross-device persistence or hosted run history.

## D-006 — Real tools and test doubles separated
- **Status:** Planned default.
- **Why:** Deterministic offline testing is useful without credentials, but live user-facing flow must be honest.
- **Tradeoff:** Requires clearly labelling live versus mock results.
