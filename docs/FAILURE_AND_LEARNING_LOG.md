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

### FL-002 — 2026-10-27 (Stage 03)
- **ID/date/stage:** FL-002 / 2026-10-27 / Stage 03
- **Symptom / exact sanitized error:** `AssertionError: assert '' == 'cisa.gov'` and `assert 0.75 > 0.8` in `test_source_quality_filter_dedup_and_length`.
- **Impact:** When a `SourceItem` was constructed from raw data without an explicit `domain` field, the domain remained empty string `""` even though a valid URL was present, causing domain-based credibility scoring and downstream presentation to lose domain metadata.
- **Root cause and evidence:** `SourceQualityFilter.process` and `compute_source_quality_score` relied on `source.domain` without falling back to parsing the hostname from `source.url`.
- **Fix:** Updated `compute_source_quality_score` to use `source.domain.lower() if source.domain else urlparse(source.url).netloc.lower()`, updated `SourceQualityFilter.process` to automatically populate `item.domain = urlparse(canon).netloc.lower()`, and adjusted content depth threshold to 50 chars for extracted text.
- **Regression test/command:** `pytest tests/test_tools.py::test_source_quality_filter_dedup_and_length`
- **Observed result after fix:** `30 passed in 4.50s`.
- **Remaining risk:** None; domain is guaranteed to be extracted from canonical URL if omitted.
