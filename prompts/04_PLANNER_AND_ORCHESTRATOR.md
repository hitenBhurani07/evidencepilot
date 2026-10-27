# STAGE 04 — Visible planner and agent orchestration

## Tasks
1. Implement a visibly inspectable single-agent workflow: validate request → create bounded plan → select tools per plan step → search → fetch/extract selected sources → normalize/filter evidence → synthesize → validate structured answer → return run metadata.
2. The planner should output a small number of typed steps, each containing purpose, suggested tool, expected evidence, and completion condition. Cap number of steps, source count, and iteration count to control latency/cost.
3. Tool selection must be meaningful: search for discovery; fetch/extract selected URLs for detail; optionally repeat search with a refined query only when results are weak and budget allows.
4. Include deterministic fallbacks for failures such as no results and partial failures. A failed optional source should not erase valid results. If all tools fail, return a clear structured failure response instead of made-up research.
5. Expose workflow events (planned, tool selected, call completed/failed, evidence filtered, synthesis completed) without revealing secrets or sensitive full page content. Log request/run ID, latency, tool status, counts, and categorized errors.
6. Include a dry-run/fake-provider mode for offline testing, clearly marked as fake. Never confuse dry-run output with live research.
7. Unit and integration tests: tool selection, plan bounds, ordering, partial failure, all-tools failure, and cancellation/timeout behavior if applicable.

## Acceptance gate
The code visibly implements planning/orchestration and invokes both tools in the real path. Tests prove execution order and failure recovery. No infinite loop and no arbitrary unbounded provider calls.
