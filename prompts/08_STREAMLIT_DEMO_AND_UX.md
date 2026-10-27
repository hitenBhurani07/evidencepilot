# STAGE 08 — Thin demo interface and local end-to-end verification

## Tasks
1. Add a small Streamlit interface only if it improves demonstrability without hiding the engineering workflow. A CLI/API-only demo is acceptable if clearer. Keep UI simple.
2. The interface must actually accept an editable research question, have a working submit/run control, show plan and tool activity, render findings/sources/confidence/limitations, and display errors usefully. Avoid hard-coded output and placeholder buttons.
3. Add progress/status and prevent accidental repeated submissions while one run is active. Keep tool result rendering readable and sources clickable.
4. Verify all interactive controls work, invalid/empty questions are rejected, long responses remain readable, and no secret appears in UI/logs.
5. Provide exact Windows PowerShell and generic terminal commands for setup, environment activation, tests, and app start. Do not assume user has Linux or shell experience; explain each manual command in README.
6. If browser preview is available, use it to inspect actual running app interactions. If not available, run API/CLI tests and state the visual check was not run.
7. Capture no fake UI screenshots. Do not upload anything externally.

## Acceptance gate
A clean local start is verified. All visible controls have real behavior. One end-to-end happy path and one controlled failure are demonstrated through the actual pipeline or safely labelled mock mode.
