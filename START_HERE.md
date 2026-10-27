# START HERE — EvidencePilot Antigravity Pack

**Purpose:** Build the Predixion AI Platform Engineering assignment in Antigravity, with autonomous implementation wherever the IDE can act and exact, safe human handoffs for things that require your account, permission, or credentials.

## Before opening Antigravity

1. Download and extract this ZIP into a normal folder, for example `EvidencePilot`.
2. Open that extracted folder as the Antigravity workspace.
3. Do not paste API keys into the chat. Do not put secrets into screenshots, prompts, markdown, source code, or Git.
4. Read this file once. Then give Antigravity the short launch instruction below.

## Launch instruction to paste into Antigravity

> Read `prompts/00_MASTER_IMPLEMENTATION_CONTRACT.md` and `docs/PROJECT_CHARTER.md` first. Then execute the project stages in order by reading one `prompts/0N_*.md` file at a time. You may continue automatically after a stage passes its acceptance gate; do not ask me to approve routine coding decisions. Before every stage, inspect the current repository and `docs/STATUS.md`. Run real checks, inspect outputs, fix and retest failures, and update the living Markdown records. If a task requires a human-only action (account signup/login, copying an API key, browser approval, creating a remote repository, granting permissions, or consent to billing), stop only at that point and show me a numbered click-by-click handoff with the exact website, page, fields, safe choices, what not to click, and how to tell you it is done. Continue all independent work before that blocker. Never request a secret in chat. After I complete the manual steps, resume from `docs/STATUS.md` without restarting or asking me to repeat information. Do not claim a test, API, deployment, or GitHub push succeeded unless verified.

## What Antigravity can and cannot do

**Usually autonomous inside the workspace:** inspect and edit files; implement Python code; create tests and documentation; install project dependencies if terminal permission is granted; run tests and the app; inspect tracebacks; fix defects; verify links/flows locally; create sample outputs clearly labelled as actual runs or fixtures; run a code/security review; prepare Git commits.

**May require you:** create/sign into third-party accounts; accept provider terms; solve CAPTCHA or MFA; generate/copy API secrets; decide whether to consent to terms that allow provider data use; grant browser/terminal permissions; create or authorize a GitHub remote; make a repository public; upload a video; enable Drive/YouTube viewing; submit the form. The exact boundaries depend on your Antigravity permissions and account state. The agent must not pretend it performed an unavailable action.

## Project target

Build **EvidencePilot**, a focused AI research agent with an explicit plan, at least two tools, source filtering, source-backed structured answers, failure handling, and an evaluation set of at least five queries. A thin Streamlit interface is optional and should not distract from the agent itself.

## Credential/default decisions

- LLM: Google Gemini API, using a model that AI Studio explicitly offers under the free tier for your project.
- Search: use Tavily's free API as the default unless Antigravity detects an already-configured search provider in the workspace. Tavily documents 1,000 free API credits/month with no credit card required; verify the current terms during setup. See `docs/FREE_API_SETUP_GUIDE.md`.
- Page content: a lightweight extraction library with ordinary HTTP requests and timeouts; do not scrape sites aggressively or bypass access restrictions.
- Persistence: local files / SQLite only if justified. **Firebase is not required by this assignment.** Do not create a Firebase project unless a demonstrated requirement makes a remote database necessary.
- No paid services, paid model, cloud deployment, Docker, vector database, or multi-agent framework by default.

## Manual-task protocol

When blocked by a manual task, Antigravity must create/update `docs/HUMAN_ACTIONS.md` with: task ID, why it is needed, exact steps, values/choices to use, unsafe choices to avoid, expected completion evidence (never the secret itself), what it will do immediately after you finish, and current blocker status. It should send you one compact instruction, not a vague request like “configure the API.”

After you reply that the steps are done, it must verify through a safe smoke test (without printing credentials), update the docs, and continue.

## Deadline

The assignment deadline in the supplied brief is **30 October 2026, 6:00 PM IST**. Prioritize a working, tested minimum complete solution and its submission artifacts over optional polish.

Resume EvidencePilot exactly where work stopped. First inspect the repository and read `docs/STATUS.md` to identify the current stage, completed acceptance gates, outstanding tasks, and blockers. Review the relevant stage prompt, decision log, error log, and existing test results.

## When Antigravity stops because of a limit
**Restart or continue the agent in the same project folder and paste this prompt: **
Do not restart the project or redo completed stages blindly. Verify the current state, identify the first unmet acceptance criterion, and continue from there. Implement, test, inspect failures, fix them, and retest. Update all relevant Markdown records before proceeding. Continue automatically through passing stages. Stop only for genuine human-only actions and provide precise numbered instructions. Never claim success without verification.