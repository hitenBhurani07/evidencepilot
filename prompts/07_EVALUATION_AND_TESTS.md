# STAGE 07 — Evaluation suite and evidence-backed test report

## Tasks
1. Ensure automated tests cover schema/config, planner/tool selection, both tools, source filtering, citation validation, malformed provider output, timeouts/retries, all-tools failure, prompt injection, SSRF protections, and low evidence.
2. Define at least five evaluation queries from different types: comparative research, entity discovery, technical pros/cons, time-sensitive research (date-aware), and unanswerable/ambiguous or failure-triggering query.
3. For every evaluation query, record expected behavior, tools expected to run, grounding requirements, edge cases, actual run outcome, observed defects, and fix status. Use live calls only when credentials/quota are available; otherwise clearly label as not run / mocked.
4. Where possible, generate actual outputs through the running pipeline and save 2–3 sample outputs in `artifacts/`. Make timestamps and run mode explicit. Remove personal data and all secrets.
5. Build a short rubric: evidence relevance, citation traceability, answer coverage, uncertainty honesty, failure robustness, output schema validity. Score only evidence actually observed. Explain that a small evaluation set is illustrative, not a scientific benchmark.
6. Do not optimize scores by hard-coding benchmark queries or fixture responses into the live path.

## Acceptance gate
At least five evaluation queries and expected behavior are recorded; test command/results and caveats are honest; two or three sample outputs exist or their blocker is clearly documented; regressions pass.
