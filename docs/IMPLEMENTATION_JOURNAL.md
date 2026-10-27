# Implementation Journal

> Chronological record of actual work. Antigravity must add dated entries after each implementation stage and significant debugging session. Do not prefill imaginary outcomes.

## Entry template
- **Date/time and stage:**
- **Goal:**
- **Files changed:**
- **What changed and why:**
- **Commands/checks run:**
- **Observed result:**
- **Defects found/fixed:**
- **Decision log references:**
- **Acceptance gate:** PASS / FAIL / BLOCKED
- **Next step:**

---

### Entry 01 — 2026-10-27 (Stage 01: Requirements, Environment Audit, and Repository Skeleton)
- **Date/time and stage:** 2026-10-27T14:38:00+05:30 / Stage 01
- **Goal:** Unpack and flatten workspace structure, audit runtime environment (Python 3.14.0, Git 2.51.2, virtualenv), initialize local git repository, construct clean skeleton (`src/evidencepilot/`, `tests/`, `artifacts/`), establish safe config and secret masking with regression test suite.
- **Files changed:**
  - `docs/REQUIREMENTS_AND_ACCEPTANCE.md`: Added comprehensive traceability matrix mapping R01-R19 to components and verification criteria.
  - `src/evidencepilot/__init__.py`, `config.py`, `schemas/__init__.py`, `providers/__init__.py`, `tools/__init__.py`, `agent/__init__.py`, `storage/__init__.py`
  - `tests/__init__.py`, `tests/test_config.py`
  - `artifacts/.gitkeep`
  - `pyproject.toml`, `requirements.txt`
  - `docs/FAILURE_AND_LEARNING_LOG.md`
- **What changed and why:**
  - Reorganized workspace so project root contains all docs, prompts, and source modules.
  - Created `.venv` on Python 3.14 and installed core dependencies (`pydantic`, `pytest`, `python-dotenv`, `httpx`, `beautifulsoup4`, `google-genai`).
  - Implemented `AppConfig` with strict secret masking in `mask_secret` and `safe_summary` to prevent accidental credential leakage in logs or exceptions.
  - Implemented validation methods `validate_for_live_llm()` and `validate_for_live_search()` which point to documentation without leaking any keys.
- **Commands/checks run:**
  - `python --version; git --version; pip --version` -> Python 3.14.0, Git 2.51.2, pip 26.0.1
  - `git init; git check-ignore -v .env` -> Confirmed `.env` is ignored by `.gitignore`
  - `python -m venv .venv` -> Virtual environment initialized successfully
  - `.venv/Scripts/python -m pip install ...` -> Successfully installed dependencies
  - `.venv/Scripts/pytest` -> 6 tests passed in 0.19s
- **Defects found/fixed:**
  - `test_mask_secret_none_or_empty` caught whitespace string `"   "` evaluating truthy and returning `[SET (len=0) ***]`. Fixed by checking `if not secret or not secret.strip(): return "[NOT SET]"`. Logged as FL-001.
- **Decision log references:** D-001, D-002, D-005, D-006.
- **Acceptance gate:** PASS
- **Next step:** Stage 02 — Core schemas, configuration validation, and provider adapters.

---

### Entry 02 — 2026-10-27 (Stage 02: Schemas, Configuration, and Provider Contracts)
- **Date/time and stage:** 2026-10-27T14:42:00+05:30 / Stage 02
- **Goal:** Implement Pydantic domain models, provider abstraction protocols (`LLMProvider`, `SearchProvider`), sanitized exception hierarchy, Gemini wrapper with JSON schema enforcement, Tavily search adapter with bounded inputs and timeout control, deterministic test fakes (`FakeLLMProvider`, `FakeSearchProvider`), and unit tests.
- **Files changed:**
  - `src/evidencepilot/schemas/research.py`: `ResearchRequest`, `PlanStep`, `ResearchPlan`, `SourceItem`, `Finding`, `RunMetadata`, `StructuredAnswer`.
  - `src/evidencepilot/schemas/__init__.py`: Exported schemas.
  - `src/evidencepilot/providers/base.py`: Protocols (`LLMProvider`, `SearchProvider`), `SearchResult`, sanitized exceptions (`ProviderError`, `AuthError`, `RateLimitError`, `NetworkError`, `SchemaValidationError`).
  - `src/evidencepilot/providers/fakes.py`: `FakeLLMProvider` and `FakeSearchProvider`.
  - `src/evidencepilot/providers/gemini.py`: Production `GeminiProvider` using official `google-genai` SDK with markdown fence stripping and client-side Pydantic validation.
  - `src/evidencepilot/providers/tavily.py`: Production `TavilySearchProvider` with input bounds and graceful malformed result skipping.
  - `src/evidencepilot/providers/__init__.py`: Exported providers.
  - `tests/test_schemas.py`: Schema validation unit tests.
  - `tests/test_providers.py`: Provider adapter, fake, and error mapping tests.
  - `docs/DECISION_LOG.md`: Added D-007.
- **What changed and why:**
  - Separated interface contracts from vendor APIs to allow deterministic offline testing and future provider substitution without touching core agent logic.
  - Implemented sanitized error mapping so no API key or sensitive header can leak via exception messages or logs.
  - Guaranteed that structured responses from LLMs undergo strict local Pydantic validation.
- **Commands/checks run:**
  - `.venv\Scripts\pytest` -> 19 passed in 1.32s
  - `Test-Path .env` -> Confirmed `.env` does not exist in workspace, ensuring offline test integrity
- **Defects found/fixed:** None.
- **Decision log references:** D-003, D-004, D-006, D-007.
- **Acceptance gate:** PASS
- **Next step:** Stage 03 — Research tools and source quality (search tool, page content extractor, safe URL filter, quality scoring).

---

### Entry 03 — 2026-10-27 (Stage 03: Research Tools and Source Quality)
- **Date/time and stage:** 2026-10-27T14:47:00+05:30 / Stage 03
- **Goal:** Implement the two core research tools (web search tool and page content extractor), strict SSRF protection (scheme checks, private IP blocking, manual redirect validation), source quality heuristics and deduplication, and prompt injection defense fixtures.
- **Files changed:**
  - `src/evidencepilot/tools/url_policy.py`: `validate_target_url`, `is_ip_private_or_local`, `canonicalize_url`.
  - `src/evidencepilot/tools/extractor.py`: `PageExtractor`, `ExtractionResult` with timeout, byte streaming limit (512 KB), redirect validation, and HTML sanitization.
  - `src/evidencepilot/tools/search.py`: `SearchTool` translating provider search outputs into normalized `SourceItem`s.
  - `src/evidencepilot/tools/source_scorer.py`: `SourceQualityFilter`, `compute_source_quality_score` with domain and content depth scoring.
  - `src/evidencepilot/tools/__init__.py`: Exported tools.
  - `tests/test_tools.py`: 11 new tests covering SSRF blocks, redirect loops, byte limits, extraction, deduplication, and prompt injection isolation.
  - `docs/FAILURE_AND_LEARNING_LOG.md`: Added FL-002.
  - `docs/DECISION_LOG.md`: Added D-008 and D-009.
- **What changed and why:**
  - Implemented SSRF and malicious redirect protection to ensure the agent can never query internal/local IP addresses or cloud metadata endpoints.
  - Implemented text extraction that removes scripts and noisy layout elements to prevent execution of untrusted code and mitigate prompt injection attacks.
  - Implemented source canonicalization and deduplication to maintain clean, non-redundant evidence sets.
- **Commands/checks run:**
  - `.venv\Scripts\pytest` -> 30 passed in 4.50s.
- **Defects found/fixed:**
  - FL-002: In `SourceQualityFilter`, sources without explicit domain field were not auto-extracting domain from URL. Fixed by parsing domain from URL in `compute_source_quality_score` and `process()`.
- **Decision log references:** D-008, D-009.
- **Acceptance gate:** PASS
- **Next step:** Stage 04 — Planner and Orchestrator.

---

### Entry 04 — 2026-10-27 (Stage 04: Planner and Orchestrator)
- **Date/time and stage:** 2026-10-27T14:51:00+05:30 / Stage 04
- **Goal:** Implement explicit single-agent planning (`ResearchPlanner`), execution orchestration (`ResearchOrchestrator`), event bus observability (`EventBus`), budget bounds enforcement, partial tool failure handling, and zero-evidence structured refusal.
- **Files changed:**
  - `src/evidencepilot/agent/events.py`: `WorkflowEventType`, `WorkflowEvent`, `EventBus`.
  - `src/evidencepilot/agent/planner.py`: `ResearchPlanner` with step bounds and deterministic fallback.
  - `src/evidencepilot/agent/orchestrator.py`: `ResearchOrchestrator` coordinating search, page fetch, quality filtering, and failure recovery.
  - `src/evidencepilot/agent/__init__.py`: Exported agent classes.
  - `src/evidencepilot/providers/fakes.py`: Fixed `FakeSearchProvider` default results check.
  - `tests/test_agent.py`: 6 tests covering happy path, event sequence, partial page extraction failure, zero-evidence refusal, and query budget caps.
  - `docs/FAILURE_AND_LEARNING_LOG.md`: Added FL-003.
  - `docs/DECISION_LOG.md`: Added D-010.
- **What changed and why:**
  - Visible plan is generated before any tool runs; each step has explicit purpose, tool, and input.
  - Connected real tools (Search and PageExtractor) in the execution path.
  - Ensured that partial failures (one URL failing) do not crash the run, and total failures (no evidence) produce a structured zero-confidence response without hallucinations.
- **Commands/checks run:**
  - `.venv\Scripts\pytest` -> 36 passed in 3.17s.
- **Defects found/fixed:**
  - FL-003: In `FakeSearchProvider`, passing `default_results=[]` was evaluated as falsy, triggering the default non-empty list fallback. Fixed by checking `if default_results is not None:`.
- **Decision log references:** D-010.
- **Acceptance gate:** PASS
- **Next step:** Stage 05 — Grounded Synthesis and Structured Results.

---

### Entry 05 — 2026-10-27 (Stage 05: Grounded Synthesis and Structured Results)
- **Date/time and stage:** 2026-10-27T14:54:00+05:30 / Stage 05
- **Goal:** Implement evidence-grounded answer synthesis (`ResearchSynthesizer`), strict citation set validation, untrusted prompt injection delimiter isolation, calibrated confidence rationale, deterministic markdown report formatting (`format_answer_markdown`), and integration into `ResearchOrchestrator`.
- **Files changed:**
  - `src/evidencepilot/agent/synthesizer.py`: `ResearchSynthesizer`, `SynthesisPayload`, `format_answer_markdown`.
  - `src/evidencepilot/agent/orchestrator.py`: Integrated `ResearchSynthesizer` into default synthesis step.
  - `src/evidencepilot/agent/__init__.py`: Exported synthesizer symbols.
  - `tests/test_synthesis.py`: 5 tests covering happy path, hallucinated citation stripping, ungrounded finding confidence penalty, provider error fallback, and markdown export.
  - `docs/DECISION_LOG.md`: Added D-011.
- **What changed and why:**
  - Grounded answer synthesis exclusively in sources collected during current execution.
  - Enforced client-side set validation of all cited `source_ids`, stripping hallucinated references and penalizing ungrounded claims.
  - Added clean GitHub Markdown presentation formatter for publication-ready reports.
- **Commands/checks run:**
  - `.venv\Scripts\pytest` -> 41 passed in 2.23s.
- **Defects found/fixed:** None.
- **Decision log references:** D-011.
- **Acceptance gate:** PASS
- **Next step:** Stage 06 — Reliability, Security, and Logging.
