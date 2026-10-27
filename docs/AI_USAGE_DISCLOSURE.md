# AI Tool Usage Disclosure

**Date:** 2026-10-27  
**Project:** EvidencePilot — AI Research Agent

---

## Tools used

### Google Antigravity (primary development assistant)

Antigravity was used throughout the entire implementation:

- **Project scaffolding:** Generated initial directory structure, `.gitignore`, `.env.example`, `pyproject.toml`, and `requirements.txt`
- **Code generation:** Produced first drafts of all Python modules (`schemas/`, `providers/`, `tools/`, `agent/`, `config.py`, `health.py`, `logging.py`, `run_logger.py`, `utils/retry.py`)
- **Test generation:** Wrote all test files (`test_schemas.py`, `test_config.py`, `test_providers.py`, `test_tools.py`, `test_security.py`, `test_synthesis.py`, `test_agent.py`, `test_reliability_logging.py`, `test_evaluation.py`)
- **Terminal execution:** Ran `pytest`, `pip install`, `git` commands; inspected logs; fixed failures
- **Bug fixing:** Identified and corrected Unicode encoding issues in `cli.py`, test assertion mismatches, and FakeLLMProvider gaps
- **Documentation:** Generated `README.md`, `docs/SECURITY_RISKS.md`, `docs/EVALUATION_RUBRIC.md`, `docs/DEMO_RUNBOOK.md`
- **Evaluation:** Designed 5-query evaluation suite, rubric, and scoring

---

## AI-assisted areas (all files generated with Antigravity assistance)

| File / Component | AI Role |
|---|---|
| `src/evidencepilot/schemas/research.py` | Generated; reviewed for field bounds correctness |
| `src/evidencepilot/config.py` | Generated; reviewed secret masking logic |
| `src/evidencepilot/providers/gemini.py` | Generated; reviewed error-mapping coverage |
| `src/evidencepilot/providers/tavily.py` | Generated; reviewed HTTP status handling |
| `src/evidencepilot/providers/fakes.py` | Generated; reviewed dummy data completeness |
| `src/evidencepilot/tools/url_policy.py` | Generated; reviewed SSRF coverage |
| `src/evidencepilot/tools/extractor.py` | Generated; reviewed redirect-validation loop |
| `src/evidencepilot/tools/source_scorer.py` | Generated; reviewed scoring heuristics |
| `src/evidencepilot/agent/planner.py` | Generated |
| `src/evidencepilot/agent/orchestrator.py` | Generated; reviewed budget enforcement |
| `src/evidencepilot/agent/synthesizer.py` | Generated; reviewed citation stripping |
| `src/evidencepilot/agent/events.py` | Generated |
| `src/evidencepilot/logging.py` | Generated; reviewed masking patterns |
| `src/evidencepilot/run_logger.py` | Generated; reviewed structured JSON fields |
| `src/evidencepilot/health.py` | Generated |
| `src/evidencepilot/utils/retry.py` | Generated; reviewed non-retryable error handling |
| `app.py` (Streamlit) | Generated; reviewed all interactive controls |
| `cli.py` | Generated; fixed Windows encoding bug |
| `scripts/run_evaluation.py` | Generated; reviewed query types and expected outcomes |
| All `tests/*.py` | Generated; reviewed assertions and acceptance criteria |
| All `docs/*.md` | Generated with human direction on content requirements |

---

## Human review and ownership

The project owner:

1. **Reviewed all stage acceptance criteria** against the prompts before accepting each stage as complete
2. **Executed terminal commands** as instructed to verify outputs (test results, health checks, Streamlit startup)
3. **Provided the API key setup instructions** and will complete credential configuration before live testing
4. **Will record and upload the demo video** when the live environment is ready
5. **Will create the GitHub remote repository** following the step-by-step instructions in `docs/HUMAN_ACTIONS.md`
6. **Will submit the assignment form** after reviewing the final checklist

The owner should ensure they can explain:
- The 5-stage pipeline: plan → search → fetch → filter → synthesize
- Why SSRF protections are needed and how they work
- The prompt injection boundary (`<evidence>` tags + UNTRUSTED DATA BOUNDARY system instruction)
- How the retry utility prevents credential waste on auth failures
- The difference between mock and live mode outputs and why the evaluation is labelled PASS_WITH_CAVEAT for temporal queries

---

## Validation

- **Offline tests:** 70 tests pass deterministically without any live API calls
- **Live-provider tests:** NOT RUN (credentials not yet configured); instructions provided in `docs/FREE_API_SETUP_GUIDE.md`
- **Mock mode tests:** All evaluation queries and CLI/Streamlit paths verified in mock mode
- **AI-generated code correctness:** Verified by running actual pytest, inspecting output, and fixing failures before marking stages complete

---

## Final honesty check

- [x] The list of AI tools is complete (Google Antigravity is the only AI assistant used)
- [x] Assisted components are identified (all files; no component is claimed as fully manual)
- [x] No unsupported claim of fully manual authorship — all code was AI-generated
- [ ] I can explain the main architecture, flow, failure handling, tests, and tradeoffs ← **owner must verify before submission**
