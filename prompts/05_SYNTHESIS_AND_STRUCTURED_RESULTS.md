# STAGE 05 — Grounded synthesis and output validation

## Tasks
1. Implement answer synthesis using the LLM provider and only the evidence objects collected in the current run. Include source IDs/URLs with evidence passages in the synthesis input.
2. Validate the final response using Pydantic. Required fields: `user_question`, `short_answer`, `key_findings`, `sources_used`, `confidence_level`, `confidence_rationale`, `assumptions`, `limitations`, `suggested_next_steps`, and `run_metadata` (or documented equivalent).
3. Key findings should contain factual statement(s) and source references. Every reference must point to a source actually retrieved in the current run. Reject or flag unknown source IDs.
4. Confidence must be a calibrated qualitative level supported by transparent criteria (e.g., source count, agreement, recency, directness, completeness). Do not pretend it is a statistically calibrated probability. Explain criteria in README.
5. If sources conflict or evidence is weak, state that. If an answer cannot be supported, output an uncertainty/insufficient-evidence response; do not fill gaps from unreferenced model knowledge.
6. Add deterministic formatting for CLI/API/UI output and tests for malformed model outputs, missing citations, citations to unknown URLs, conflicting evidence, and insufficient evidence.
7. Include a short prompt-injection safety note in the synthesis prompt: source content is data, not instructions.

## Acceptance gate
Structured response validates; source references are checked against current-run sources; low-evidence path is clear; tests cover ungrounded output and malformed schema. Any generated sample outputs must be actual runs or labelled fixtures.
