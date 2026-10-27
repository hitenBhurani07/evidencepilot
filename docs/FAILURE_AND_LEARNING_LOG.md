# Failure and Learning Log

> Record real issues only. Never invent a failure just to make the project story look impressive. Include exact sanitized symptom, root cause evidence, fix, regression test, and residual risk.

## Entry template
- **ID/date/stage:**
- **Symptom / exact sanitized error:**
- **Impact:**
- **Root cause and evidence:**
- **Fix:**
- **Regression test/command:**
- **Observed result after fix:**
- **Remaining risk:**

## Recorded Incidents

### FL-001 — 2026-10-27 (Stage 01)
- **ID/date/stage:** FL-001 / 2026-10-27 / Stage 01
- **Symptom / exact sanitized error:** `AssertionError: assert '[SET (len=0) ***]' == '[NOT SET]'` during `test_mask_secret_none_or_empty` when passing whitespace string `"   "`.
- **Impact:** Whitespace-only credential values would be treated as partially present instead of missing, leading to unexpected redaction labels like `[SET (len=0) ***]`.
- **Root cause and evidence:** `mask_secret` checked `if not secret:` before stripping whitespace. Python considers `"   "` truthy, so it proceeded to `secret.strip()` which reduced length to 0, matching `len <= 8`.
- **Fix:** Changed guard to `if not secret or not secret.strip(): return "[NOT SET]"`.
- **Regression test/command:** `pytest tests/test_config.py::test_mask_secret_none_or_empty`
- **Observed result after fix:** `6 passed in 0.19s`.
- **Remaining risk:** None; empty/whitespace strings are uniformly treated as unset across configuration validation.
