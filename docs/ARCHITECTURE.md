# EvidencePilot Architecture

## High-level flow

```text
User question
  -> Request validation
  -> Planner (bounded typed steps)
  -> Orchestrator
       -> Tool 1: web search (Tavily adapter)
       -> Tool 2: fetch/extract page content (safe HTTP + extractor)
  -> Normalize, deduplicate, and score evidence quality
  -> Gemini synthesis using only retrieved evidence
  -> Pydantic validation + citation ID verification
  -> Structured answer + run metadata + UI/CLI/API
```

## Responsibilities
- **Config:** model/provider identifiers, timeouts, budgets, secret loading, safe startup errors.
- **Schemas:** stable typed contracts for requests, plan, source, finding, answer, events.
- **Provider adapter:** translates Gemini/Tavily APIs into internal contracts; isolates vendor changes.
- **Tools:** search and page extraction. Each has input bounds, timeouts, categorized failures, tests.
- **Planner/orchestrator:** chooses tools, limits steps, tracks events, handles partial and total failures.
- **Evidence filter:** URL canonicalization, deduplication, empty/low-value filtering, source metadata.
- **Synthesis:** writes answer using only current-run evidence and requested output schema.
- **Validation:** Pydantic plus citation checks. LLM output is never trusted solely because it was requested as JSON.
- **Presentation:** optional Streamlit; not business logic.
- **Evaluation:** deterministic tests, mocked integration tests, separate live smoke tests, five-plus query evaluation set.

## Why one agent
The assignment recommends a clear single-agent design. A transparent planner/orchestrator is easier to reason about and test than a multi-agent system and limits latency/cost.

## Why no Firebase
No user accounts or durable multi-user state are required. Local output artifacts and logs are sufficient for a take-home demo. Firebase would add console setup, access rules, credentials, network dependency, and more failure modes without satisfying an explicit requirement.

## Free-first and replaceability
Gemini and Tavily clients are hidden behind small provider interfaces. Offline test doubles do not call the network. The real path must never silently switch to fakes. Model selection is configuration; only a model available on the account's free tier is permitted by default.

## Security boundary
Fetched web content is untrusted. Fetch tool must reject unsafe URLs and internal IPs, limit redirects/bytes/time, and re-check redirect targets. Tool output is evidence only—not instructions. Provider secrets stay in environment configuration and never enter output/logs.
