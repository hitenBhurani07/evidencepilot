# Operations and Tradeoffs

## Reliability
Use bounded timeouts/retries, provider error classes, structured outputs, safe fallbacks, and a run id. A rate limit should not cause endless retries. Authentication errors should fail fast.

## Security
Secrets only from local environment settings; no secrets in logs or docs. Use a fetch allowlist/policy to avoid internal network access and unsafe URL schemes. Retrieved content is untrusted.

## Cost and quota
Use free-tier-only models and search credits, one smoke test before broad live evaluation, bounded queries/pages/tokens, and no automatic billing or upgrade. If quota is exhausted, record a blocker and keep offline tests running.

## Latency tradeoff
A bounded plan with a small number of searches and page fetches is more reproducible and cheaper than open-ended agent loops. Add concurrency only if measurements justify it.

## Data persistence
Local sample outputs and sanitized logs keep setup small. Remote storage is outside scope; Firebase setup would add credentials/rules and cloud dependencies without satisfying an explicit requirement.

## Confidence
Use qualitative, explainable confidence with a rationale, not fake numeric precision. It reflects retrieved evidence quantity/relevance/consistency, not calibrated probability.

## Production boundary
The assignment should demonstrate production-minded reasoning, not claim fully production-grade security, uptime, or compliance. Describe what would be needed for actual production deployment.
