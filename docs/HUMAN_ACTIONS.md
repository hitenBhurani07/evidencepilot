# Human Actions Queue — Maintained by Antigravity

> Antigravity must keep this file current. It should list only actions that truly require the user. Never store API keys, tokens, passwords, recovery codes, or screenshots containing them here.

## Status vocabulary
- `NOT NEEDED`: no user action required.
- `PENDING`: exact steps have been provided, waiting for user.
- `DONE — VERIFY`: user says done; agent must perform safe verification.
- `VERIFIED`: agent confirmed success without revealing secrets.
- `BLOCKED`: user action cannot be completed because of a clear external issue; state what is blocked.

## Queue

### H-001 — Gemini API key
- Status: `PENDING ONLY WHEN LIVE LLM TEST IS NEEDED`
- Why: live synthesis requires a valid Gemini key; offline tests do not.
- Steps: see `docs/FREE_API_SETUP_GUIDE.md` → “LLM: Google Gemini API (free tier)”.
- What to return: reply that the key is saved in local `.env`; **do not send the key**.
- Agent next action: validate `.env` is ignored, run one minimal smoke test without printing the key, record outcome, continue.

### H-002 — Tavily API key
- Status: `PENDING ONLY WHEN LIVE SEARCH TEST IS NEEDED`
- Why: live web discovery requires a search key; deterministic fake can support offline tests.
- Steps: see `docs/FREE_API_SETUP_GUIDE.md` → “Search: Tavily free API”.
- What to return: reply that the key is saved in local `.env`; **do not send the key**.
- Agent next action: run one minimal search smoke test, redact logs, record outcome, continue.

### H-003 — GitHub remote
- Status: `NOT NEEDED UNTIL LOCAL IMPLEMENTATION PASSES`
- Why: remote creation/authorization may require your account.
- Agent next action: inspect `git remote -v`; if no remote, prepare exact steps and ask only after code/docs/tests are ready. Never commit secrets or push without authorization.

### H-004 — Demo video / external sharing
- Status: `NOT NEEDED UNTIL FINAL DEMO IS READY`
- Why: recording and changing external view permissions may require your input/account.
- Agent next action: prepare runbook and script; ask you to record/upload only when code is verified, unless authorized browser actions are genuinely available.

## Handoff template (Antigravity must follow this format)
1. **Task / why it is needed**
2. **Where to go** (exact URL or local file path)
3. **Exact steps** (numbered clicks/actions and exact fields)
4. **Use these choices** (safe/free choice)
5. **Do not click/do** (paid upgrade, billing, publish, destructive options)
6. **How to confirm completion** (non-secret evidence)
7. **What I will do next automatically**
8. **Reply phrase** (simple confirmation that does not include the secret)
