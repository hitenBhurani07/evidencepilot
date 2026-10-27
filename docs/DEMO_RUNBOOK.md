# Demo Runbook (3–5 minutes)

> Finalize only after the implementation is actually running. Do not record fake or staged outputs as live.

## Suggested timeline
- **0:00–0:25 — Problem:** State that EvidencePilot accepts a research question and must return grounded findings, sources, uncertainty, and limitations.
- **0:25–0:55 — Architecture:** Show the planner/orchestrator and the two tools: web search and page extraction. Explain why a single-agent flow was selected.
- **0:55–2:10 — Happy path:** Enter a representative question, show visible plan/tool activity, show sources and evidence-backed findings, click a source, explain confidence rationale.
- **2:10–3:05 — Failure/edge path:** Demonstrate an invalid/ambiguous question, simulated timeout in a test mode, empty result, or a safe prompt-injection fixture. Clearly label mock/failure mode if not a live-provider failure.
- **3:05–3:50 — Tests/evaluation:** Show test command/results and evaluation document with at least five queries.
- **3:50–4:30 — Engineering decisions:** Explain free-tier guardrails, schema validation, source filtering, logs, and why Firebase/multi-agent/cloud deployment were omitted.
- **4:30–5:00 — Limitations:** State known limits and next improvements honestly.

## Recording checklist
- Hide `.env` and any terminal output that could expose secrets.
- Use non-sensitive sample questions.
- Ensure the app has finished loading and UI elements are functional.
- Record readable text and visible source links.
- Show the actual tests/results rather than claiming them verbally only.
- Save video locally first; upload/share only when ready.
- Verify link access in an incognito/signed-out window if appropriate. Keep repo, video, evaluation, and sample-output links in the final submission checklist.
