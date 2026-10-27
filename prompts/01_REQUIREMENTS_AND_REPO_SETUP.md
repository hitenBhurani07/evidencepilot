# STAGE 01 — Requirements, environment audit, and repository skeleton

Read the master contract first. Work only on requirements translation and skeleton.

## Tasks
1. Inspect assignment PDF text captured in project docs and all existing workspace files. If the assignment PDF itself is present in the workspace, inspect it directly and preserve its actual requirements.
2. Check local Python version, Git availability, and workspace state. Do not install tools blindly; record exact checks and propose commands if permissions are unavailable.
3. Update `docs/REQUIREMENTS_AND_ACCEPTANCE.md` with a checklist mapped to observable code/test/demo evidence. Tag each item `EXPLICIT`, `ENGINEERING DECISION`, or `OPTIONAL`.
4. Create the smallest suitable project structure: source package, provider adapters, tools, agent workflow, schemas/config, tests, docs, artifacts. Avoid extra folders unless justified.
5. Add `pyproject.toml` or pinned requirements, `.gitignore`, `.env.example` (placeholders only), and a minimal `README.md` section for local setup. Do not add real API keys.
6. Start/refresh the living docs. Record only decisions actually made now. Add a first entry to implementation journal.
7. Add a small configuration test proving missing keys produce a clear, redacted message rather than an accidental crash or secret leak.

## Explicitly do not do yet
Do not build the full agent, do not add Firebase, do not create cloud resources, do not create/push a remote repository, and do not choose an unverified Gemini model.

## Acceptance gate
- Requirements have traceable acceptance checks.
- Skeleton and `.gitignore` exist; `.env` is ignored and `.env.example` has placeholders only.
- Python/Git/environment checks are recorded with actual results.
- Offline test command is documented and at least one skeleton/config test runs.
- Human-only tasks are listed in `docs/HUMAN_ACTIONS.md` only if actually required.
