# STAGE 02 — Schemas, configuration, and provider contracts

## Tasks
1. Inspect existing files first. Use Pydantic schemas for request, plan steps, normalized source, evidence/finding, final structured answer, provider errors, and run metadata. Choose sensible length/count bounds.
2. Add one `Settings`/configuration module that reads environment variables and validates settings. Secret values must never appear in reprs/logs/errors. Keep model/provider identifiers configurable.
3. Implement narrow protocols/interfaces for `LLMProvider` and `SearchProvider`; include deterministic fake implementations for tests.
4. Implement the Gemini provider wrapper using current official `google-genai` documentation. Do not yet call paid-only models or assume a model id. Ensure structured responses are parsed and then locally validated.
5. Default real search integration to Tavily only after checking current docs and noting in the decision log why its no-card free tier suits this deadline. If the user already has another configured provider in the local environment, do not reveal its values; preserve it only if name/configuration can be identified locally.
6. Add `.env.example` keys such as `GEMINI_API_KEY=`, `GEMINI_MODEL=`, `TAVILY_API_KEY=`, plus bounded non-secret settings. `.env` must remain ignored.
7. Add tests for schema validation, missing configuration, malformed provider payload, and sanitized errors.
8. Before live API setup is needed, use `docs/FREE_API_SETUP_GUIDE.md`. Continue with fakes while waiting for human setup.

## Human handoff behavior
If no valid API key is present in local environment, create a task in `docs/HUMAN_ACTIONS.md` that points to the free setup guide. Explain that the key must be placed in local `.env` or IDE environment settings and never pasted into chat. Do not block offline tests on this.

## Acceptance gate
Schema tests pass; config values are separated from source; fakes work without credentials; no live API success claimed unless tested; docs describe free-tier limitations and privacy implications.
