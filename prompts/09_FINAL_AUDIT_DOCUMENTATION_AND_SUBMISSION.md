# STAGE 09 — Final audit, documentation, and submission handoff

## Tasks
1. Run the complete offline test suite; run live smoke tests only if credentials and quotas are available. Record exact commands, return status, and concise observed outcomes.
2. Inspect code for hidden mocks in live paths, hard-coded output, stale/dead features, fabricated citations, unsafe URL fetches, secrets, bad exception handling, excessive dependencies, and mismatched docs.
3. Verify `.env` is ignored; inspect tracked files with `git status` and safe secret scanner. Never print a detected secret's value. If a secret was committed, treat it as compromised: instruct user to rotate it and remove it from history only with explicit approval and safe procedure.
4. Complete README: problem, requirements, architecture diagram/flow, tools, setup, free API signup, environment variables, run/test commands, output schema, reliability/security choices, evaluation results, limitations, tradeoffs, AI-assisted development disclosure, future improvements.
5. Create two or three sample outputs from actual runs, label time/model/mode; save generated evaluation notes. Never label mock output as live.
6. Finish `docs/DEMO_RUNBOOK.md` for 3–5 minutes: show input, visible plan, search + extraction tools, source-backed response, one edge/failure path, tests/evaluation, limitations.
7. Update `docs/AI_USAGE_DISCLOSURE.md` based on actual activity. The user should review and ensure they can explain the architecture. Do not write unsupported claims of independent authorship.
8. If a GitHub remote does not exist, prepare everything locally and create a `docs/HUMAN_ACTIONS.md` handoff with exact steps to create a repository. Do not assume remote permissions. If authorized and tool access exists, ask before making the repo public or pushing externally unless the user has explicitly instructed that action.
9. Verify repository URL, demo video URL, viewing permissions, evaluation document, and sample outputs only when their real values are available. Do not submit the form. Provide a final checklist for user review and form submission.

## Acceptance gate
Every explicit assignment requirement maps to concrete evidence; all tests have honest statuses; README reproduces setup; no keys/secrets are tracked; demo/evaluation/sample outputs are ready or clearly marked blocked with exact human steps.
