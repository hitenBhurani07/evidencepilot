# Human Actions Queue — Maintained by Antigravity

> Antigravity keeps this file current. It lists only actions that truly require user intervention. Never store API keys, tokens, passwords, recovery codes, or screenshots containing them here.

## Status vocabulary
- `NOT NEEDED`: no user action required.
- `PENDING`: exact steps have been provided, waiting for user.
- `DONE — VERIFY`: user says done; agent must perform safe verification.
- `VERIFIED`: agent confirmed success without revealing secrets.
- `BLOCKED`: user action cannot be completed because of a clear external issue; state what is blocked.

---

## Active Queue

### H-001 — Gemini API Key (Optional for offline; Required for live mode)
- **Status**: `NOT NEEDED FOR SUBMISSION` (Offline mock pipeline is 100% verified with 70 tests passing)
- **Why**: Live synthesis requires a Google AI Studio key.
- **Reference**: See `docs/FREE_API_SETUP_GUIDE.md` if live testing is desired.

### H-002 — Tavily Search API Key (Optional for offline; Required for live mode)
- **Status**: `NOT NEEDED FOR SUBMISSION` (Offline mock pipeline is 100% verified with 70 tests passing)
- **Why**: Live search requires a Tavily key.
- **Reference**: See `docs/FREE_API_SETUP_GUIDE.md` if live testing is desired.

---

### H-003 — GitHub Remote Repository Creation & Push
- **Status**: `PENDING`
- **Task / why it is needed**: The local git repository contains all 9 completed stages, tests, docs, and artifacts. A remote repository URL is required for the final assignment submission.

1. **Where to go**:
   - Open your web browser and navigate to: https://github.com/new (log in if prompted).

2. **Exact steps (Numbered clicks & actions)**:
   1. In the **Repository name** field, type: `evidencepilot` (or `predixion-evidencepilot`).
   2. In the **Description (optional)** field, type: `Grounded Autonomous AI Research Agent with Multi-Step Tool Verification`.
   3. Choose visibility: Select **Public** (or **Private** if you intend to invite evaluators as collaborators).
   4. Under **Initialize this repository with**:
      - ⚠️ **DO NOT check** "Add a README file" (we already have a complete README locally).
      - ⚠️ **DO NOT check** "Add .gitignore" (we already have `.gitignore` configured locally).
      - ⚠️ **DO NOT check** "Choose a license" (leave as None for now).
   5. Click the green button: **Create repository**.
   6. On the quick setup page that appears, copy the **HTTPS** clone URL (e.g., `https://github.com/<your-username>/evidencepilot.git`).
   7. In your local Windows PowerShell terminal inside `c:\Users\hiten\prexidion_ai`, run:
      ```powershell
      git remote add origin <PASTE_YOUR_COPIED_URL_HERE>
      git branch -M master
      git push -u origin master
      ```

3. **Safe choices**:
   - Do NOT check any template initialization boxes on GitHub.
   - Use HTTPS authentication or GitHub CLI credentials.

4. **Do not click/do**:
   - Do not push `.env` (it is already ignored by `.gitignore`).
   - Do not make changes directly on GitHub before pushing the local branch.

5. **How to confirm completion**:
   - Verify that all files (README, src/, tests/, docs/, artifacts/) are visible on GitHub.

6. **What I will do next automatically**:
   - Update `docs/SUBMISSION_CHECKLIST.md` and `docs/STATUS.md` with confirmation.

7. **Reply phrase**:
   - Reply in chat: `GitHub repo pushed: https://github.com/<your-username>/evidencepilot`

---

### H-004 — Demo Video Recording (3–5 minutes)
- **Status**: `PENDING`
- **Task / why it is needed**: The assignment requires a 3–5 minute video demonstrating a happy path research query, visible tool execution, grounded citations, and an edge/failure path.

1. **Where to go**:
   - Follow the detailed script and timing in `docs/DEMO_RUNBOOK.md`.
   - Tool of choice: OBS Studio, Windows Game Bar (Win+G), or Loom (free tier).

2. **Exact sequence to record (4 minutes total)**:
   - **Minute 0:00–0:45**: Introduction & Architecture overview (show README and CLI/Streamlit launcher).
   - **Minute 0:45–2:15**: Happy path in Streamlit UI: Run query `Compare solid-state batteries vs lithium-ion for EV applications` (Mock or Live). Highlight the visible `ResearchPlan`, tool extraction activity, and structured citations `[1]`, `[2]`.
   - **Minute 2:15–3:15**: Edge/Failure case: Input obscure unanswerable query (e.g. `What is the secret code inside Project X-999-Z?`). Show how the agent refuses to hallucinate, records zero confidence, and logs data gaps in `contradictions_or_uncertainties`.
   - **Minute 3:15–4:00**: Show test suite execution in terminal (`pytest tests/` -> 70 passed) and mention evaluation rubric (`scripts/run_evaluation.py`).

3. **Where to upload**:
   - Upload to YouTube (Unlisted), Google Drive (Ensure setting is **"Anyone with the link can view"**), or Loom.

4. **Reply phrase**:
   - Reply in chat: `Demo video recorded: <VIDEO_URL>`

---

## Completed Human Actions
*(None yet)*
