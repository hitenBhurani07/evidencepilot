# Scaling Roadmap — Only After Assignment Core Works

## Current target: focused take-home prototype
- Single-agent planner/orchestrator
- Two research tools
- Free-tier provider APIs and strict request budgets
- Local run artifacts/logs
- Typed output and citation validation
- Offline test suite and five-plus query evaluation

## Reasonable future work (not required for submission)
1. Provider abstraction with robust switching/fallback after policy checks.
2. Improved source-quality evaluation and claim-level evidence matching.
3. Cached retrieval with clear freshness/TTL and privacy rules.
4. Background jobs and async tool calls where latency benefits are measured.
5. Optional SQLite run history if local persistence is needed; Firebase only for a justified multi-user/cloud requirement.
6. Deployment with secret manager, authentication, quotas, monitoring, alerting, rate limiting, and privacy/security review.
7. Broader offline/online benchmark with human-reviewed labels.

## Not now
Do not implement cloud deployment, Firebase, vector DB, multi-agent planning, long-term memory, paid observability, or async execution before the explicit acceptance checklist passes. These add complexity and possible cost without being required.
