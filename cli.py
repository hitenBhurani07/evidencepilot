"""EvidencePilot CLI — command-line research interface.

Usage (from project root, with .venv active):
    .venv\\Scripts\\python cli.py "Your research question here"
    .venv\\Scripts\\python cli.py "What are the risks of AI in healthcare?" --mock
    .venv\\Scripts\\python cli.py --health

Arguments:
    query           Research question (required unless --health)
    --mock          Force offline/mock mode regardless of credentials
    --max-queries   Maximum search queries to run (default: 2)
    --max-pages     Maximum pages to fetch (default: 3)
    --health        Print system health check and exit
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Allow running from project root without installation
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Force UTF-8 output on Windows so Unicode characters display correctly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]

load_dotenv(dotenv_path=".env", override=False)

from evidencepilot.agent.orchestrator import ResearchOrchestrator
from evidencepilot.agent.events import EventBus, WorkflowEvent, WorkflowEventType
from evidencepilot.agent.synthesizer import format_answer_markdown
from evidencepilot.config import AppConfig
from evidencepilot.health import check_system_health
from evidencepilot.providers.base import AuthError, NetworkError, ProviderError, RateLimitError
from evidencepilot.providers.fakes import FakeLLMProvider, FakeSearchProvider
from evidencepilot.run_logger import RunLogger
from evidencepilot.schemas.research import ResearchRequest


def _print_health(cfg: AppConfig) -> None:
    health = check_system_health(cfg)
    print("\n=== EvidencePilot Health Check ===")
    print(f"  Status            : {health['status']}")
    print(f"  Python version    : {health['python_version']}")
    print(f"  SSRF protection   : {health['ssrf_protection']}")
    print(f"  Gemini configured : {health['gemini_configured']} (model: {health['gemini_model']})")
    print(f"  Tavily configured : {health['tavily_configured']}")
    print(f"  Budget - searches : {health['budgets']['max_search_queries']}")
    print(f"  Budget - pages    : {health['budgets']['max_fetch_pages']}")
    print(f"  Budget - timeout  : {health['budgets']['request_timeout_seconds']}s")
    print("==================================\n")


def _print_separator(char: str = "-", width: int = 70) -> None:
    print(char * width)


def _build_orchestrator(cfg: AppConfig, force_mock: bool):
    events: list[WorkflowEvent] = []
    bus = EventBus(listener=lambda ev: events.append(ev))

    if not force_mock and cfg.gemini_api_key and cfg.tavily_api_key:
        from evidencepilot.providers.gemini import GeminiProvider
        from evidencepilot.providers.tavily import TavilySearchProvider
        llm = GeminiProvider(api_key=cfg.gemini_api_key, model_name=cfg.gemini_model)
        search = TavilySearchProvider(api_key=cfg.tavily_api_key, timeout_seconds=cfg.request_timeout_seconds)
        mode = "LIVE"
    else:
        llm = FakeLLMProvider()
        search = FakeSearchProvider()
        mode = "MOCK_OFFLINE"

    orch = ResearchOrchestrator(llm_provider=llm, search_provider=search, event_bus=bus)
    return orch, events, mode


def main() -> int:
    parser = argparse.ArgumentParser(
        description="EvidencePilot -- AI research agent CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("query", nargs="?", default=None, help="Research question")
    parser.add_argument("--mock", action="store_true", help="Force offline/mock mode")
    parser.add_argument("--max-queries", type=int, default=2, help="Max search queries (default: 2)")
    parser.add_argument("--max-pages", type=int, default=3, help="Max pages to fetch (default: 3)")
    parser.add_argument("--health", action="store_true", help="Print health check and exit")
    args = parser.parse_args()

    cfg = AppConfig.load()

    if args.health:
        _print_health(cfg)
        return 0

    if not args.query:
        parser.print_help()
        print("\nERROR: A research question is required. Example:")
        print('  .venv\\Scripts\\python cli.py "What are the risks of AI in healthcare?"')
        return 1

    query = args.query.strip()
    if len(query) < 3:
        print("ERROR: Research question is too short (minimum 3 characters).")
        return 1

    print(f"\nEvidencePilot Research Agent")
    _print_separator()

    try:
        req = ResearchRequest(
            query=query,
            max_search_queries=max(1, min(args.max_queries, 5)),
            max_pages_to_fetch=max(1, min(args.max_pages, 8)),
        )
    except Exception as e:
        print(f"ERROR -- Invalid request: {e}")
        return 1

    orch, events, mode = _build_orchestrator(cfg, force_mock=args.mock)
    run_logger = RunLogger()
    run_logger.log_start(query_length=len(query))

    print(f"  Mode   : {mode}")
    print(f"  Query  : {query}")
    print(f"  Budget : {req.max_search_queries} searches, {req.max_pages_to_fetch} pages")
    _print_separator()

    print("\nRunning research... (this may take a few seconds in live mode)\n")

    try:
        answer = orch.execute(req)
    except AuthError as e:
        print(f"\nAUTH ERROR: {e}")
        print("-> Your API key is invalid or missing. See docs/FREE_API_SETUP_GUIDE.md")
        return 1
    except RateLimitError as e:
        print(f"\nRATE LIMIT: {e}")
        print("-> Free quota exhausted. Wait a few minutes and try again.")
        return 1
    except NetworkError as e:
        print(f"\nNETWORK ERROR: {e}")
        print("-> Check your internet connection and try again.")
        return 1
    except ProviderError as e:
        print(f"\nPROVIDER ERROR: {e}")
        return 1

    # Tool activity
    event_labels = {
        WorkflowEventType.PLAN_CREATED: "[PLAN]",
        WorkflowEventType.TOOL_CALLED: "[TOOL]",
        WorkflowEventType.TOOL_COMPLETED: "[ OK ]",
        WorkflowEventType.TOOL_FAILED: "[FAIL]",
        WorkflowEventType.EVIDENCE_FILTERED: "[FILT]",
        WorkflowEventType.SYNTHESIS_STARTED: "[SYNTH]",
        WorkflowEventType.RUN_COMPLETED: "[DONE]",
    }
    print("Tool activity:")
    for ev in events:
        label = event_labels.get(ev.event_type, "[    ]")
        print(f"  {label} {ev.message}")

    print()
    _print_separator()

    # Results
    conf_pct = round(answer.confidence_score * 100)
    mock_tag = "[MOCK]" if answer.metadata.is_mock_run else "[LIVE]"
    print(f"\nCONFIDENCE : {conf_pct}%  {mock_tag}")
    print(f"LATENCY    : {answer.metadata.total_latency_seconds}s")
    print(f"SOURCES    : {len(answer.sources)} retrieved, {answer.metadata.sources_used_in_synthesis} used\n")

    print("EXECUTIVE SUMMARY")
    _print_separator("-", 50)
    print(answer.short_answer)
    print()

    print("KEY FINDINGS")
    _print_separator("-", 50)
    for i, f in enumerate(answer.key_findings, 1):
        cites = ", ".join(f"[{s}]" for s in f.source_ids) or "(no citation)"
        print(f"{i}. {f.statement}")
        print(f"   Sources: {cites} | Confidence: {round(f.confidence*100)}%")
    print()

    if answer.sources:
        print("SOURCES")
        _print_separator("-", 50)
        for s in answer.sources:
            print(f"  [{s.id}] {s.title}")
            print(f"       {s.url}")
            print(f"       Quality: {round(s.quality_score*100)}% | {s.domain}")

    print()
    if answer.limitations:
        print("LIMITATIONS")
        for lim in answer.limitations:
            print(f"  * {lim}")

    _print_separator()

    # Save markdown report
    md_path = Path("artifacts") / f"cli_report_{int(time.time())}.md"
    md_path.parent.mkdir(exist_ok=True)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(format_answer_markdown(answer))
    print(f"\nReport saved: {md_path}")

    run_logger.log_complete(
        confidence=answer.confidence_score,
        total_sources=answer.metadata.total_sources_found,
        sources_used=answer.metadata.sources_used_in_synthesis,
        tool_calls=answer.metadata.tool_calls_count,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
