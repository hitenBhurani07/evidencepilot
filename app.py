"""EvidencePilot Streamlit Demo — Stage 08.

Run (from project root, with .venv active):
    .venv\\Scripts\\streamlit run app.py

Requires .env with GEMINI_API_KEY and TAVILY_API_KEY for live mode.
Without credentials the app runs in offline/mock mode automatically.
"""

from __future__ import annotations

import time
from typing import Optional

import streamlit as st
from dotenv import load_dotenv

# Load .env if present (keys never logged or displayed)
load_dotenv(dotenv_path=".env", override=False)

from evidencepilot.agent.orchestrator import ResearchOrchestrator
from evidencepilot.agent.events import EventBus, WorkflowEvent, WorkflowEventType
from evidencepilot.agent.synthesizer import format_answer_markdown
from evidencepilot.config import AppConfig, ConfigError
from evidencepilot.health import check_system_health
from evidencepilot.providers.fakes import FakeLLMProvider, FakeSearchProvider
from evidencepilot.providers.base import AuthError, RateLimitError, NetworkError, ProviderError
from evidencepilot.schemas.research import ResearchRequest, StructuredAnswer
from evidencepilot.run_logger import RunLogger

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="EvidencePilot — AI Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------

if "running" not in st.session_state:
    st.session_state.running = False
if "last_answer" not in st.session_state:
    st.session_state.last_answer = None
if "last_events" not in st.session_state:
    st.session_state.last_events = []
if "last_error" not in st.session_state:
    st.session_state.last_error = None

# ---------------------------------------------------------------------------
# Config + health check (cached per session)
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner=False)
def _load_config() -> AppConfig:
    return AppConfig.load()


cfg = _load_config()
health = check_system_health(cfg)

# ---------------------------------------------------------------------------
# Sidebar — configuration and health
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("🔬 EvidencePilot")
    st.caption("Explainable AI Research Agent")
    st.divider()

    # Health status
    overall_status = health["status"]
    if "READY_FOR_LIVE" in overall_status:
        st.success("✅ Live API mode active")
    elif "PARTIALLY" in overall_status:
        st.warning("⚠️ Partially configured — some features use mock mode")
    else:
        st.info("🧪 Offline / Mock mode — no live API keys detected")

    with st.expander("System health", expanded=False):
        st.json({
            "ssrf_protection": health["ssrf_protection"],
            "gemini_configured": health["gemini_configured"],
            "gemini_model": health["gemini_model"],
            "tavily_configured": health["tavily_configured"],
            "budgets": health["budgets"],
        })

    st.divider()
    st.markdown("**Budget settings**")
    max_queries = st.slider("Max search queries", 1, 5, 2)
    max_pages = st.slider("Max pages to fetch", 1, 6, 3)

    st.divider()
    st.caption("Credentials are loaded from `.env` only. Keys are never displayed or logged.")
    st.caption("See `docs/FREE_API_SETUP_GUIDE.md` for setup instructions.")

# ---------------------------------------------------------------------------
# Main UI
# ---------------------------------------------------------------------------

st.markdown("# 🔬 EvidencePilot")
st.markdown(
    "Submit a research question and receive a **grounded, cited, structured answer** "
    "built from real web evidence — or a transparent refusal if evidence is unavailable."
)
st.divider()

# Query input
query_input = st.text_area(
    label="Research question",
    placeholder="e.g. What are the main risks of deploying LLMs in healthcare settings?",
    height=100,
    max_chars=500,
    key="query_input",
    disabled=st.session_state.running,
)

col_run, col_clear = st.columns([1, 5])
with col_run:
    run_button = st.button(
        "🚀 Run Research" if not st.session_state.running else "⏳ Running…",
        disabled=st.session_state.running,
        type="primary",
        key="run_button",
    )
with col_clear:
    clear_button = st.button(
        "Clear",
        disabled=st.session_state.running,
        key="clear_button",
    )

if clear_button:
    st.session_state.last_answer = None
    st.session_state.last_events = []
    st.session_state.last_error = None
    st.rerun()

# ---------------------------------------------------------------------------
# Research execution
# ---------------------------------------------------------------------------

def _build_orchestrator() -> tuple[ResearchOrchestrator, list[WorkflowEvent]]:
    """Return a configured orchestrator + empty event log."""
    events: list[WorkflowEvent] = []
    bus = EventBus(listener=lambda ev: events.append(ev))

    if cfg.gemini_api_key and cfg.tavily_api_key:
        # Live mode
        from evidencepilot.providers.gemini import GeminiProvider
        from evidencepilot.providers.tavily import TavilySearchProvider
        llm = GeminiProvider(api_key=cfg.gemini_api_key, model_name=cfg.gemini_model)
        search = TavilySearchProvider(api_key=cfg.tavily_api_key, timeout_seconds=cfg.request_timeout_seconds)
    else:
        # Offline / mock mode
        llm = FakeLLMProvider()
        search = FakeSearchProvider()

    orch = ResearchOrchestrator(
        llm_provider=llm,
        search_provider=search,
        event_bus=bus,
    )
    return orch, events


if run_button:
    # Validate query before starting
    stripped = (query_input or "").strip()
    if len(stripped) < 3:
        st.error("❌ Please enter a research question of at least 3 characters.")
    else:
        st.session_state.running = True
        st.session_state.last_answer = None
        st.session_state.last_events = []
        st.session_state.last_error = None

        run_logger = RunLogger()
        run_logger.log_start(query_length=len(stripped))

        with st.status("🔍 Running research…", expanded=True) as status_box:
            try:
                req = ResearchRequest(
                    query=stripped,
                    max_search_queries=max_queries,
                    max_pages_to_fetch=max_pages,
                )

                orch, events = _build_orchestrator()

                st.write("📋 Generating research plan…")
                answer: StructuredAnswer = orch.execute(req)

                # Log events to sidebar
                st.session_state.last_events = events
                st.session_state.last_answer = answer

                run_logger.log_complete(
                    confidence=answer.confidence_score,
                    total_sources=answer.metadata.total_sources_found,
                    sources_used=answer.metadata.sources_used_in_synthesis,
                    tool_calls=answer.metadata.tool_calls_count,
                )

                status_box.update(label="✅ Research complete!", state="complete")

            except AuthError as auth_err:
                st.session_state.last_error = (
                    "🔑 **Authentication error:** Your API key is invalid or not set.\n\n"
                    f"See `docs/FREE_API_SETUP_GUIDE.md` to configure credentials.\n\n"
                    f"_(Error category: {auth_err.provider_name} — auth rejected)_"
                )
                run_logger.log_error("auth", "auth_rejected", is_retryable=False)
                status_box.update(label="❌ Authentication failed", state="error")

            except RateLimitError as rl_err:
                st.session_state.last_error = (
                    "⏱️ **Rate limit or quota exceeded.**\n\n"
                    "Your free API quota may be exhausted. Wait a few minutes and try again.\n\n"
                    f"_(Provider: {rl_err.provider_name})_"
                )
                run_logger.log_error("search_or_llm", "rate_limit", is_retryable=True)
                status_box.update(label="❌ Rate limit hit", state="error")

            except NetworkError as net_err:
                st.session_state.last_error = (
                    "🌐 **Network error.**\n\n"
                    "Could not reach the API. Check your internet connection and try again.\n\n"
                    f"_(Provider: {net_err.provider_name})_"
                )
                run_logger.log_error("network", "connection_failure", is_retryable=True)
                status_box.update(label="❌ Network error", state="error")

            except ProviderError as prov_err:
                st.session_state.last_error = (
                    f"⚠️ **Provider error.**\n\n{prov_err}\n\n"
                    "Check configuration and retry."
                )
                run_logger.log_failed("provider_error")
                status_box.update(label="❌ Provider error", state="error")

            except ValueError as val_err:
                st.session_state.last_error = f"❌ **Invalid input:** {val_err}"
                run_logger.log_failed("validation_error")
                status_box.update(label="❌ Validation error", state="error")

            except Exception as exc:
                st.session_state.last_error = (
                    f"⚠️ **Unexpected error.**\n\nSomething went wrong during research. "
                    f"Please try again.\n\n_(Error type: {type(exc).__name__})_"
                )
                run_logger.log_failed("unexpected_error")
                status_box.update(label="❌ Error", state="error")

            finally:
                st.session_state.running = False

        st.rerun()

# ---------------------------------------------------------------------------
# Results rendering
# ---------------------------------------------------------------------------

if st.session_state.last_error:
    st.error(st.session_state.last_error)

elif st.session_state.last_answer:
    answer: StructuredAnswer = st.session_state.last_answer

    # Confidence badge
    conf_pct = round(answer.confidence_score * 100)
    if conf_pct >= 70:
        conf_color = "🟢"
    elif conf_pct >= 40:
        conf_color = "🟡"
    else:
        conf_color = "🔴"

    run_mode_badge = "🧪 Mock mode" if answer.metadata.is_mock_run else "🌐 Live mode"

    st.markdown(f"## 📄 Research Results  {conf_color} {conf_pct}% confidence  |  {run_mode_badge}")
    st.caption(f"Query: *{answer.question}* | Sources found: {answer.metadata.total_sources_found} | Used: {answer.metadata.sources_used_in_synthesis} | Latency: {answer.metadata.total_latency_seconds}s")

    # Executive summary
    st.markdown("### Executive Summary")
    st.info(answer.short_answer)

    # Key findings
    st.markdown("### Key Findings")
    for i, finding in enumerate(answer.key_findings, 1):
        citation_str = ", ".join(f"`[{sid}]`" for sid in finding.source_ids) if finding.source_ids else "*(no citation)*"
        conf_f = round(finding.confidence * 100)
        st.markdown(f"**{i}.** {finding.statement}  \n_Sources: {citation_str} — {conf_f}% confidence_")

    # Sources table
    if answer.sources:
        st.markdown("### Verified Sources")
        for s in answer.sources:
            score_bar = "█" * int(s.quality_score * 10) + "░" * (10 - int(s.quality_score * 10))
            with st.expander(f"**{s.id}** — {s.title} (`{s.domain}`) {score_bar} {round(s.quality_score*100)}%"):
                st.markdown(f"🔗 [{s.url}]({s.url})")
                if s.snippet:
                    st.caption(s.snippet[:400])

    # Assumptions / Limitations / Next Steps
    cols = st.columns(3)
    with cols[0]:
        if answer.assumptions:
            st.markdown("**Assumptions**")
            for a in answer.assumptions:
                st.markdown(f"- {a}")
    with cols[1]:
        if answer.limitations:
            st.markdown("**Limitations**")
            for lim in answer.limitations:
                st.markdown(f"- {lim}")
    with cols[2]:
        if answer.next_steps:
            st.markdown("**Next Steps**")
            for ns in answer.next_steps:
                st.markdown(f"- {ns}")

    # Confidence rationale
    with st.expander("Confidence rationale"):
        st.markdown(answer.confidence_rationale)

    # Tool activity timeline
    if st.session_state.last_events:
        with st.expander("Tool activity log", expanded=False):
            for ev in st.session_state.last_events:
                icon = {
                    WorkflowEventType.REQUEST_VALIDATED: "✅",
                    WorkflowEventType.PLAN_CREATED: "📋",
                    WorkflowEventType.STEP_STARTED: "▶",
                    WorkflowEventType.TOOL_CALLED: "🔧",
                    WorkflowEventType.TOOL_COMPLETED: "✔",
                    WorkflowEventType.TOOL_FAILED: "❌",
                    WorkflowEventType.EVIDENCE_FILTERED: "🔍",
                    WorkflowEventType.SYNTHESIS_STARTED: "✨",
                    WorkflowEventType.RUN_COMPLETED: "🏁",
                    WorkflowEventType.RUN_FAILED: "💥",
                }.get(ev.event_type, "•")
                st.caption(f"{icon} {ev.message}")

    # Download markdown report
    md_report = format_answer_markdown(answer)
    st.download_button(
        label="📥 Download report as Markdown",
        data=md_report,
        file_name=f"evidencepilot_report_{int(time.time())}.md",
        mime="text/markdown",
        key="download_btn",
    )

else:
    st.markdown(
        "> Enter a research question above and click **Run Research** to start.\n\n"
        "> In **mock/offline mode** (no API keys), the agent runs a deterministic simulation "
        "so you can verify the full UI and workflow without any credentials."
    )
