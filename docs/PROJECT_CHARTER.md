# Project Charter — EvidencePilot

## Mission
Build a compact, reliable, explainable AI research agent that researches a user question with explicit planning, at least two tools, evidence filtering, source-grounded synthesis, failure handling, and evaluation.

## Explicit submission requirements from the assignment
- Source-code repository
- README: setup, architecture, design decisions, limitations, future work
- Short demo video (3–5 minutes) showing one happy path and one failure/edge case
- Brief evaluation document with at least five test queries, expected behavior, and actual observations
- Two or three sample outputs
- Form submission details include GitHub repository link, README confirmation, technical challenge, demo link, AI tool usage disclosure

## Scope: must-have
Question input; visible plan; tool selection; real search plus content extraction; normalized sources; filtering/deduplication; structured answer; citations tied to source IDs; confidence rationale; assumptions/limitations/next steps; timeouts/retries/failure response; prompt-injection awareness; logs; offline tests; evaluation notes; setup docs.

## Reasonable engineering decisions
Python; Pydantic; official Gemini SDK using a free-tier available model; Tavily free tier as default search provider; a light extraction library; custom single-agent orchestration; Pytest; small Streamlit UI or CLI; local logs/artifacts.

## Non-goals unless needed and authorized
Firebase/cloud database; user accounts; payments; vector database/RAG index; multi-agent workflow; autonomous browser crawling; deployment to cloud; Docker/Kubernetes; production observability SaaS; paid API tier; submitting the application form.

## Success definition
A reviewer can clone the repo, follow the README, configure free-tier credentials safely, run a live research query, inspect the workflow and sources, run offline tests, inspect evaluation and sample outputs, and understand tradeoffs.

## Deadline
30 October 2026, 6:00 PM IST. Complete minimum requirements before optional enhancements.
