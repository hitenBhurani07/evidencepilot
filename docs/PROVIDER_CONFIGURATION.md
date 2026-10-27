# Provider Configuration

## LLM provider
- Provider: Google Gemini API
- SDK: official `google-genai` Python SDK after verifying current docs
- Environment variables: `GEMINI_API_KEY`, `GEMINI_MODEL`
- Secret availability: user reported a Gemini key; local configuration not yet verified by this blueprint
- Live smoke test: NOT RUN
- Free-tier rule: select only a model explicitly available on the project's free tier; do not enable billing or upgrade tier
- Docs: https://ai.google.dev/gemini-api/docs/libraries ; https://ai.google.dev/gemini-api/docs/api-key ; https://ai.google.dev/gemini-api/docs/pricing ; https://ai.google.dev/gemini-api/docs/rate-limits

## Search provider
- Default: Tavily Search API
- SDK/docs: https://docs.tavily.com/documentation/quickstart
- Pricing docs: https://www.tavily.org/pricing.html
- Current documented free offer: 1,000 credits/month with no credit card; verify at signup
- Environment variable: `TAVILY_API_KEY`
- Live smoke test: NOT RUN

## Environment
`.env.example` must contain empty values/placeholders only. `.env` is local and must be ignored by Git. Never print key values or send them in chat. Do not include API secrets in tests, sample outputs, logs, screen recordings, or evaluation documents.

## Verification status
This blueprint package has not executed application code or API calls. Antigravity must record actual evidence after implementation. Free tiers and provider terms can change; recheck official pages at setup.
