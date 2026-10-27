# EvidencePilot — AI Research Agent Assignment

This repository scaffold and prompt pack is designed for the Predixion AI Platform Engineering take-home assignment. The source assignment requires a working research agent with a visible plan, at least two tools, source-backed structured output, failure handling, an evaluation framework (at least five queries), README, demo video (3–5 minutes with a happy path and an edge/failure case), and 2–3 sample outputs.

## Start with Antigravity

1. Open the extracted folder as the Antigravity workspace.
2. Read `START_HERE.md`.
3. Paste the **Launch instruction** from that file into Antigravity.
4. Let Antigravity run stages sequentially. It should continue on its own after successful checks and stop only for a genuinely human-only action or unresolved blocker.
5. When Antigravity asks you to perform a manual task, follow `docs/HUMAN_ACTIONS.md` (the agent must keep it current). Never send API keys in chat.

## Default stack

- Python (use the installed stable version compatible with the dependencies; target Python 3.11+ unless a dependency requires otherwise)
- Google Gemini API through the official `google-genai` SDK, free-tier model selected and verified at setup
- Tavily Search API free tier by default (verify current terms at time of signup)
- Pydantic for schema validation
- Trafilatura or equivalent for web page extraction, with safe timeouts and size limits
- Pytest for automated tests
- Streamlit only as a thin demo UI if useful; the agent workflow is the priority
- Git/GitHub

## Important engineering decisions

- Use a custom single-agent orchestration workflow rather than a multi-agent framework.
- Use two substantive tools: (1) web search, (2) fetch/extract a page's readable content. A third deterministic tool (such as source-quality scoring or domain filtering) can improve transparency, but does not replace the two research tools.
- No database is needed by default. Start with deterministic run logs and stored sample outputs as local files. Add SQLite only if a requirement clearly benefits from persistence. Firebase is not part of the required solution.
- Do not use mock data in the real user-facing research path. Mocks are for deterministic tests and must be clearly identified.
- Separate offline tests from live-provider smoke tests.
- Avoid features that cost money. Never auto-upgrade an account or enable billing.

## Folder map

- `START_HERE.md`: instructions for the student and launch command
- `prompts/`: a compact master contract and stage prompts, suitable for sequential execution
- `docs/PROJECT_CHARTER.md`: objective, scope, deliverables
- `docs/REQUIREMENTS_AND_ACCEPTANCE.md`: explicit assignment requirements translated to tests
- `docs/FREE_API_SETUP_GUIDE.md`: exact human setup steps and cost guardrails
- `docs/HUMAN_ACTIONS.md`: live manual-task queue, updated by Antigravity
- `docs/ARCHITECTURE.md`: intended system shape and data flow
- `docs/DECISION_LOG.md`: decisions and rejected alternatives
- `docs/IMPLEMENTATION_JOURNAL.md`: chronological build narrative
- `docs/FAILURE_AND_LEARNING_LOG.md`: real failures, causes, fixes, regression tests
- `docs/TEST_PLAN_AND_EVALUATION.md`: test queries and evaluation discipline
- `docs/STATUS.md`: current gate, verified facts, next action
- `docs/RISK_REGISTER.md`: known risks and mitigations
- `docs/DEMO_RUNBOOK.md`: final 3–5-minute demo
- `docs/AI_USAGE_DISCLOSURE.md`: honest AI usage notes
- `docs/SCALING_ROADMAP.md`: current limits and justified future work

## API-cost and privacy note

The Gemini API has a free tier, but availability, models, quotas, and terms vary. Google documents that free-tier content may be used to improve its products. Use only non-sensitive research queries and the free-tier model/limits visible in your AI Studio account. Never enable billing or change to paid tier without explicit user consent. See `docs/FREE_API_SETUP_GUIDE.md` and the current official pricing docs linked there.

Tavily's documentation currently describes 1,000 monthly free API credits and no card requirement; verify current limits and terms before relying on them. Never commit keys. `.env` must be ignored by Git, and `.env.example` must contain placeholders only.

## Definition of done

The project is done only when the agent can run through a real research question using two tools; source URLs are visible; the output follows a validated schema; failure and prompt-injection cases are tested; at least five evaluation queries are recorded with observed outcomes; the app starts from documented steps; the final README is accurate; 2–3 outputs are preserved; a 3–5-minute video is made with viewing access; and all submission links are verified. Do not claim external actions that were not confirmed.
