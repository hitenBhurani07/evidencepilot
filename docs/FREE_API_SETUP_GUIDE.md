# Free API Setup Guide — Human Steps and Cost Guardrails

**Purpose:** When a live credential is actually needed, Antigravity must guide the student through the specific manual steps, then resume. The agent should first finish all work that can be tested offline.

## Free-first provider choices

### LLM: Google Gemini API (free tier)
Official resources:
- AI Studio API keys: https://aistudio.google.com/app/apikey
- Key guide: https://ai.google.dev/gemini-api/docs/api-key
- Pricing: https://ai.google.dev/gemini-api/docs/pricing
- Rate limits: https://ai.google.dev/gemini-api/docs/rate-limits
- SDK docs: https://ai.google.dev/gemini-api/docs/libraries

Current official pricing documentation says Gemini has a free tier with free input/output tokens for some models, limited model access, and quota/rate limits. It also states free-tier content may be used to improve Google's products. Check the actual model and quota shown in your account before selecting it. Do not send sensitive/private information through the demo.

**Manual steps when requested by Antigravity:**
1. Open https://aistudio.google.com/app/apikey and sign in to the Google account you want to use.
2. Use the UI to create or view a Gemini API key for a project. Prefer the newly created key type and the current safe defaults; follow any current instructions AI Studio shows.
3. If the UI asks you to choose a project, use/create a project for this assignment only. Do not enable billing, upgrade usage tier, or accept a paid option.
4. Copy the key only into a local `.env` file or a local IDE secret/environment configuration. **Never paste it into ChatGPT/Antigravity chat, Markdown, screenshots, source files, GitHub, or the final demo.**
5. Add it as `GEMINI_API_KEY=...` in `.env`; `GEMINI_MODEL` should be the free-tier model that Antigravity has verified in current official docs and the account UI. If model selection is not certain, leave the model blank until Antigravity asks you to choose from the available options.
6. Save the file. Tell Antigravity: **“Gemini setup completed. Do not print the key. Run the safe live smoke test and continue from docs/STATUS.md.”**
7. Antigravity must verify the key with one minimal request and log only success/failure category, model ID, and latency—not the key or full credential-bearing environment.

**Important current-docs warning:** Google documents a transition from standard keys to authorization keys and says unrestricted standard keys are rejected; current key handling has changed over time. Follow the current AI Studio flow and do not weaken restrictions or migrate configuration based on old tutorials.

### Search: Tavily free API
Official resources:
- Quickstart: https://docs.tavily.com/documentation/quickstart
- Pricing: https://www.tavily.org/pricing.html
- Platform dashboard: https://app.tavily.com/home

Tavily's current docs describe **1,000 free API credits per month with no credit card required**. Verify the current terms/quotas at signup; plans can change.

**Manual steps when requested by Antigravity:**
1. Open https://app.tavily.com/home.
2. Sign in or create an account.
3. Find API keys in the account dashboard and create/copy a key.
4. Do not choose any paid plan. If the site now requires payment details or a paid tier, stop and tell Antigravity; do not proceed.
5. Add the secret locally to `.env` as `TAVILY_API_KEY=...`.
6. Tell Antigravity: **“Tavily setup completed. Do not print the key. Run a single minimal search smoke test and continue from docs/STATUS.md.”**

## Local `.env` setup (Windows, simplest path)

Antigravity should create `.env.example` automatically. When you are asked to create `.env`:

1. In Antigravity's file explorer, duplicate `.env.example` and name the copy `.env` (or create a new file named `.env` in the project root).
2. Put the API keys into the correct fields locally; do not add quote marks unless the application instructions specifically require them. Example **with placeholders only**:

```dotenv
GEMINI_API_KEY=PASTE_YOUR_KEY_LOCALLY
GEMINI_MODEL=MODEL_ID_CONFIRMED_BY_ANTIGRAVITY
TAVILY_API_KEY=PASTE_YOUR_KEY_LOCALLY
```

3. Do not put real values in `.env.example`.
4. Save `.env`. Never upload it. Antigravity must confirm `.env` appears in `.gitignore` and is not tracked.
5. If in doubt, do not show the `.env` file in a recording or screenshot.

## Cost guardrails (mandatory)
- Never enable billing, attach payment details, choose paid-only models, upgrade provider tier, or consume paid credits without explicit user consent.
- Use one small smoke-test call per provider before a full live run.
- Set max search count, max page count, output token bounds, request timeout, and retry cap.
- Stop retries on authentication errors and avoid retry storms on 429/5xx.
- If free access is blocked, finish tests with deterministic fake providers, record live tests as `BLOCKED`, and ask before suggesting a replacement that may cost money.
- A “free API key” can still have quota, data-use, or eligibility conditions. Do not describe it as unlimited or suitable for sensitive data.

## Other manual setup only if needed

### GitHub repository
Local code can be prepared without GitHub. When needed, Antigravity should first check whether a remote already exists. If not, it must ask you to open GitHub, create a repository, choose public/private intentionally, and provide the remote URL (not any token). Do not make the repo public automatically. If evaluation requires access, confirm what visibility/share setting is acceptable before publishing.

### Demo video and links
Antigravity can write the script and verify the local demo. You must usually record the screen/video and complete external upload or sharing permissions unless its available browser tools and your explicit authorization permit those actions. Test the link in a signed-out/incognito window where appropriate.

### Firebase/database
**Not required.** Do not create a Firebase project, database, or service account for this assignment unless the user approves a justified new requirement. Research agent runs can be stored as local JSON artifacts/logs for the assignment.
