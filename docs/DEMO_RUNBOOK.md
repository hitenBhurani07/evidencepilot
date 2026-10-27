# EvidencePilot — Demo Runbook (3–5 Minutes)

> **Purpose:** Walk an evaluator through a working end-to-end demonstration of EvidencePilot in 3–5 minutes.
> No live credentials required for the mock path; live path instructions are included at the end.

---

## Original timeline (planning template)

- **0:00–0:25 — Problem:** State that EvidencePilot accepts a research question and must return grounded findings, sources, uncertainty, and limitations.
- **0:25–0:55 — Architecture:** Show the planner/orchestrator and the two tools: web search and page extraction. Explain why a single-agent flow was selected.
- **0:55–2:10 — Happy path:** Enter a representative question, show visible plan/tool activity, show sources and evidence-backed findings, click a source, explain confidence rationale.
- **2:10–3:05 — Failure/edge path:** Demonstrate an invalid/ambiguous question, simulated timeout in a test mode, empty result, or a safe prompt-injection fixture. Clearly label mock/failure mode if not a live-provider failure.
- **3:05–3:50 — Tests/evaluation:** Show test command/results and evaluation document with at least five queries.
- **3:50–4:30 — Engineering decisions:** Explain free-tier guardrails, schema validation, source filtering, logs, and why Firebase/multi-agent/cloud deployment were omitted.
- **4:30–5:00 — Limitations:** State known limits and next improvements honestly.

---

## Step-by-step commands for the demo

### Step 1 — Environment verification (30 seconds)

```powershell
# From project root, in PowerShell:
.venv\Scripts\python cli.py --health
```

**Expected output:**
```
=== EvidencePilot Health Check ===
  Status            : OFFLINE_TEST_READY (No live API keys configured)
  SSRF protection   : VERIFIED_ACTIVE
  Gemini configured : False
  Tavily configured : False
  Budget - searches : 3
  Budget - timeout  : 15s
==================================
```

### Step 2 — Full test suite (30 seconds)

```powershell
.venv\Scripts\pytest tests\ -v
# Expected: 70 passed in ~2s
```

### Step 3 — CLI happy path (45 seconds)

```powershell
.venv\Scripts\python cli.py "What are the main risks of deploying large language models in healthcare?" --mock
```

**What to observe:**
1. `Mode: MOCK_OFFLINE` (no keys needed)
2. Tool activity: `[PLAN] -> [TOOL] web_search -> [OK] -> [SYNTH] -> [DONE]`
3. Executive summary, findings with `[S1]` citations, sources table
4. `Report saved: artifacts\cli_report_...md`

### Step 4 — Controlled failure paths (30 seconds)

```powershell
.venv\Scripts\python cli.py "" --mock   # Empty query -> helpful error, exit 1
.venv\Scripts\python cli.py "ab" --mock  # Too short  -> helpful error, exit 1
```

### Step 5 — Evaluation suite (30 seconds)

```powershell
.venv\Scripts\python scripts\run_evaluation.py
# Expected: 5 PASS | 0 FAIL | 0 ERROR
```

Highlights:
- EVAL-05 (unanswerable): `confidence=0.0`, refuses to fabricate

### Step 6 — Streamlit demo (45 seconds)

```powershell
.venv\Scripts\python -m streamlit run app.py
# Open: http://localhost:8501
```

UI walkthrough:
1. Sidebar shows health, budget sliders, credential note
2. Enter: `"What are the main risks of AI in clinical decision support?"`
3. Click **Run Research** — watch spinner and tool activity
4. Observe: confidence badge, summary, findings, source expanders
5. Download markdown report
6. Clear results, try empty submit — error appears cleanly
7. `Ctrl+C` to stop

### Step 7 — Live mode (optional, requires .env credentials)

```powershell
# Copy .env.example to .env, fill in GEMINI_API_KEY and TAVILY_API_KEY
# Then run without --mock:
.venv\Scripts\python cli.py "Compare transformer and LSTM for time series forecasting"
```

> Keep max_search_queries ≤ 2 and max_pages ≤ 3 to stay within free API quota.

---

## Recording checklist

- [ ] Hide `.env` and any terminal output that could expose API keys
- [ ] Use non-sensitive, representative research questions
- [ ] Show the app fully loaded with all UI elements functional
- [ ] Record readable text and visible source links
- [ ] Show actual test results (`pytest` output) rather than claiming them verbally only
- [ ] Demonstrate both a happy path AND a controlled failure (empty query or zero-evidence)
- [ ] Save video locally first; upload/share only when ready
- [ ] Verify video link access in incognito/signed-out browser if sharing publicly

---

## Key limitations to mention during demo

1. **Mock answers** in offline mode are deterministic — not real research synthesis
2. **Temporal accuracy** (EVAL-04) requires live Tavily search to verify recency
3. **Rate limits** apply on free API tiers — stay within configured budgets
4. **Security scope** is prototype-level; see `docs/SECURITY_RISKS.md` for documented unmitigated risks

---

## File quick reference

| File | Purpose |
|---|---|
| `app.py` | Streamlit web demo |
| `cli.py` | Command-line interface |
| `scripts/run_evaluation.py` | 5-query evaluation runner |
| `artifacts/evaluation_report.json` | Combined eval results |
| `docs/SECURITY_RISKS.md` | Security mitigations and remaining risks |
| `docs/EVALUATION_RUBRIC.md` | Rubric, scores, and test coverage table |
| `docs/FREE_API_SETUP_GUIDE.md` | Free API key signup instructions |
