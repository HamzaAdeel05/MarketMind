import argparse
import json
import logging
import uuid
from pathlib import Path

from src.config import Settings
from src.llm.client import LLMClient
from src.llm.usage import UsageTracker
from src.state.research_state import ResearchState
from src.state.persistence import save_json

from src.tools.registry import ToolRegistry, ToolSpec
from src.tools.dispatcher import ToolDispatcher
from src.tools.impl.core import (
    search_information,
    retrieve_document,
    calculate_metric,
    compare_companies,
    save_research,
    generate_report,
)

from src.schemas.tools import (
    SearchArgs,
    RetrieveArgs,
    CalculateArgs,
    CompareArgs,
    SaveEvidenceArgs,
    GenerateReportArgs,
)

from src.agents.request_analyser import RequestAnalyser
from src.agents.planner import Planner
from src.agents.researcher import Researcher
from src.agents.evidence_analyst import EvidenceAnalyst
from src.agents.comparison import Comparison
from src.agents.synthesis import Synthesis
from src.agents.quality_control import QualityControl
from src.agents.report_generator import ReportGenerator

from src.approval.cli_gate import approval_gate


def build_registry():
    registry = ToolRegistry()

    registry.register(
        ToolSpec(
            "search_information",
            "Search the curated corpus for evidence.",
            SearchArgs,
            "read",
            search_information,
        )
    )

    registry.register(
        ToolSpec(
            "retrieve_document",
            "Retrieve one known corpus document.",
            RetrieveArgs,
            "read",
            retrieve_document,
        )
    )

    registry.register(
        ToolSpec(
            "calculate_metric",
            "Perform bounded deterministic arithmetic.",
            CalculateArgs,
            "compute",
            calculate_metric,
        )
    )

    registry.register(
        ToolSpec(
            "compare_companies",
            "Compare entities from evidence already stored.",
            CompareArgs,
            "compute",
            compare_companies,
        )
    )

    registry.register(
        ToolSpec(
            "save_research",
            "Persist an evidence record bound to an existing source ref.",
            SaveEvidenceArgs,
            "write",
            save_research,
        )
    )

    registry.register(
        ToolSpec(
            "generate_report",
            "Check whether mandatory questions have evidence before report generation.",
            GenerateReportArgs,
            "write",
            generate_report,
        )
    )

    return registry


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--request",
        required=True,
        help="Research request for MarketMind AI.",
    )

    args = parser.parse_args()

    settings = Settings.load()

    if len(args.request) > settings.request_max_chars:
        raise SystemExit(
            "Request exceeds configured maximum length."
        )

    run_id = f"run-{uuid.uuid4().hex[:10]}"
    run_dir = Path("runs") / run_id

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    logger = logging.getLogger("marketmind")

    usage = UsageTracker()

    llm = LLMClient(
        settings,
        usage,
        logger,
    )

    state = ResearchState(
        run_id,
        args.request,
    )

    save_json(
        run_dir,
        "request.json",
        {
            "run_id": run_id,
            "request": args.request,
        },
    )

    normalized = RequestAnalyser(llm).run(
        run_id,
        args.request,
    )

    plan = Planner(llm).run(
        run_id,
        normalized,
    )

    state.plan = plan

    save_json(
        run_dir,
        "plan.json",
        plan.model_dump(),
    )

    registry = build_registry()

    dispatcher = ToolDispatcher(
        registry,
        state,
        logger,
        settings.max_tool_calls,
    )

    Researcher(
        settings,
        dispatcher,
        state,
        logger,
    ).run()

    EvidenceAnalyst().run(state)

    comparison = Comparison(
        dispatcher
    ).run(state)

    synthesis = Synthesis(
        llm
    ).run(
        state,
        comparison,
    )

    qc = QualityControl().run(
        state,
        synthesis,
    )

    for _ in range(settings.max_repair_rounds):
        if qc["pass"]:
            break

        break

    report = ReportGenerator().run(
        state,
        synthesis,
        qc,
        usage.total_cost,
    )

    report = approval_gate(report)

    save_json(
        run_dir,
        "report.json",
        report.model_dump(),
    )

    save_json(
        run_dir,
        "state.json",
        {
            "status": state.status,
            "iteration": state.iteration,
            "evidence": [
                evidence.model_dump()
                for evidence in state.evidence
            ],
            "tool_history": state.tool_history,
            "limitations": state.limitations,
        },
    )

    save_json(
        run_dir,
        "usage.json",
        usage.as_dict(),
    )

    print(
        f"\nRun saved to {run_dir}. "
        f"Decision: {report.approval.decision}"
    )


if __name__ == "__main__":
    main()