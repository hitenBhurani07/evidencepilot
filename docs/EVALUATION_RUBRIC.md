# EvidencePilot — Evaluation Rubric and Test Report

**Stage:** 07  
**Run mode:** MOCK_OFFLINE (no live API credentials required)  
**Last run:** 2026-10-27  
**Test command:** `.venv\Scripts\pytest tests\test_evaluation.py -v`  
**Test result:** `6 passed`  
**Evaluation script:** `.venv\Scripts\python scripts\run_evaluation.py`  
**Evaluation result:** `5 PASS | 0 FAIL | 0 ERROR`

---

> [!IMPORTANT]
> All evaluations run in **offline mock mode**. Mock providers return deterministic outputs, not real web content.
> Temporal accuracy (EVAL-04), entity accuracy, and synthesis quality **cannot be verified** until live API credentials are provided.
> Scores below reflect **structural behavior**, not answer quality.

---

## Evaluation Queries

| ID | Type | Query | Expected Tools | Status |
|---|---|---|---|---|
| EVAL-01 | Comparative | Compare PostgreSQL and MongoDB for user analytics at scale | web_search, fetch_page, quality_filter | ✅ PASS |
| EVAL-02 | Entity discovery | Leading researchers in interpretable machine learning | web_search, fetch_page, quality_filter | ✅ PASS |
| EVAL-03 | Technical pros/cons | Pros and cons of Rust vs C for systems programming | web_search, fetch_page, quality_filter | ✅ PASS |
| EVAL-04 | Time-sensitive | Most significant AI safety papers in 2024 | web_search, fetch_page, quality_filter | ✅ PASS_WITH_CAVEAT |
| EVAL-05 | Unanswerable | GDP of fictional country Ruritania in 2025 | web_search | ✅ PASS (0 confidence) |

---

## Detailed Evaluation Notes

### EVAL-01 — Comparative Research
- **Expected behavior:** Returns structured comparison of both options; does not pick a winner without caveats
- **Actual:** Pipeline ran search + fetch + filter; synthesis returned structured answer with sources; confidence > 0
- **Defects observed:** None
- **Live run needed:** Yes — real comparison requires live search for current benchmarks

### EVAL-02 — Entity Discovery
- **Expected behavior:** Named entities (researchers) listed with institution/contribution grounded in sources
- **Actual:** Sources retrieved; findings reference entities from mock content; source IDs valid
- **Defects observed:** None
- **Live run needed:** Yes — real entity accuracy requires live Wikipedia/arxiv search

### EVAL-03 — Technical Pros/Cons
- **Expected behavior:** Pro/con structure with trade-offs acknowledged; balanced presentation
- **Actual:** Correct structure; findings generated from mock content; balanced language
- **Defects observed:** None
- **Live run needed:** Yes — real source diversity needed for balanced coverage

### EVAL-04 — Time-Sensitive Research
- **Expected behavior:** Notes recency limitation; citations include dates where available
- **Actual:** Mock run correctly labelled; `metadata.is_mock_run = True`; answer includes limitations
- **Defects observed:** Mock data cannot verify temporal accuracy — explicitly documented
- **Fix status:** Pending live Tavily API credential
- **Live run needed:** **YES** — this category is meaningless without live search

### EVAL-05 — Unanswerable / Failure-Triggering
- **Expected behavior:** confidence=0.0; zero sources; explicit refusal; NO hallucinated answer
- **Actual:** `confidence_score == 0.0`, `sources == []`, short_answer starts with "No verifiable evidence…"
- **Defects observed:** None — system refuses to fabricate as required
- **Hard requirement met:** ✅ No confabulation

---

## Evaluation Rubric

> **Note:** This rubric is illustrative for a small evaluation set (N=5). It is NOT a scientific benchmark.
> Scores are assigned only to behavior actually observed in test runs.

| Dimension | Description | Max Score | Mock Score | Rationale |
|---|---|---|---|---|
| Evidence relevance | Cited sources are topically relevant | 5 | 3 | Mock sources are topically named; real relevance requires live search |
| Citation traceability | Every finding cites a source ID in answer.sources | 5 | 5 | All source IDs validated by `_validate_and_sanitize_citations` |
| Answer coverage | Short answer addresses the main query intent | 5 | 3 | Deterministic fallback answers are minimal; LLM quality requires live API |
| Uncertainty honesty | Confidence score and rationale reflect evidence completeness | 5 | 5 | Zero-evidence case returns confidence=0.0; mock caveat documented |
| Failure robustness | Zero-evidence case returns structured refusal, not fabrication | 5 | 5 | EVAL-05 explicitly validates this with assertion |
| Output schema validity | StructuredAnswer passes Pydantic validation | 5 | 5 | All outputs instantiate without exception |
| **Total** | | **30** | **26/30** | |

---

## Sample Outputs

Saved to `artifacts/` directory:

- [`eval_01_mock_output.json`](../artifacts/eval_01_mock_output.json) — Comparative query
- [`eval_02_mock_output.json`](../artifacts/eval_02_mock_output.json) — Entity discovery
- [`eval_03_mock_output.json`](../artifacts/eval_03_mock_output.json) — Pros/cons
- [`eval_04_mock_output.json`](../artifacts/eval_04_mock_output.json) — Time-sensitive (PASS_WITH_CAVEAT)
- [`eval_05_mock_output.json`](../artifacts/eval_05_mock_output.json) — Unanswerable (zero-evidence)
- [`evaluation_report.json`](../artifacts/evaluation_report.json) — Combined report with rubric

---

## What Live Evaluation Would Add

When Gemini and Tavily API credentials are configured:
1. **Real answer quality** — LLM synthesis produces nuanced, human-readable answers
2. **Temporal accuracy** — Tavily search returns pages published after training cutoff
3. **Entity accuracy** — Real entity names resolved from live web pages
4. **Full rubric scores** — Evidence relevance and answer coverage can be scored at 4–5/5

To run live: copy `.env.example` to `.env`, fill in both API keys, then re-run the evaluation script.

---

## Automated Test Coverage (as of Stage 07)

| Test file | Tests | Coverage scope |
|---|---|---|
| test_schemas.py | 5 | Schema validation, field bounds, Pydantic |
| test_config.py | 6 | Config loading, secret masking, budget limits |
| test_providers.py | 8 | Fake providers, error categories, malformed output |
| test_tools.py | 11 | SSRF, URL policy, extractor, source scoring |
| test_security.py | 6 | Secret masking, retry limits, prompt injection, health |
| test_reliability_logging.py | 17 | RunLogger, API error readability, git-ignore |
| test_agent.py | 6 | Planner, orchestrator, fallback, budget caps |
| test_synthesis.py | 5 | Citation validation, hallucination stripping, markdown |
| test_evaluation.py | 6 | 5 typed eval queries + coverage checklist |
| **Total** | **70** | |

*Hard-coding benchmark queries into the live path was explicitly avoided (no fixture injection into production code paths).*
