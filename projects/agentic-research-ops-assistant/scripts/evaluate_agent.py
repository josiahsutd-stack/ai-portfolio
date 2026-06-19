from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

from agentic_research_ops_assistant import ResearchAgent  # noqa: E402


def _write_report(summary: dict[str, object], output_path: Path) -> None:
    lines = [
        "# Agent Evaluation Report",
        "",
        "Synthetic local evaluation for the Agentic Research Operations Assistant.",
        "",
        "## Summary",
        "",
        f"- Tasks: {summary['task_count']}",
        f"- Traces written: {summary['traces_written']}",
        f"- Citation rate: {summary['citation_rate']}",
        f"- Approval gate rate: {summary['approval_gate_rate']}",
        f"- Unsupported task handling: {summary['unsupported_task_handling']}",
        f"- Tool error handling: {summary['tool_error_handling']}",
        f"- Passed: {summary['passed']}",
        "",
        "## Boundaries",
        "",
        "- Deterministic local planner.",
        "- Local documents only.",
        "- Not autonomous web research.",
        "- Approval checkpoint is simulated and traceable.",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    docs_dir = PROJECT_ROOT / "sample_data" / "local_docs"
    output_dir = PROJECT_ROOT / "demo_outputs"
    output_dir.mkdir(exist_ok=True)
    trace_db = output_dir / "agent_eval_traces.sqlite"
    if trace_db.exists():
        trace_db.unlink()

    tasks = [
        "Summarize AI deployment strategies",
        "Compare multimodal AI market notes versus deployment strategies",
        "Search the live web for current AI deployment news",
        "Prepare a final report requiring approval",
        "Explain quantum banana planning assumptions",
    ]
    traces = [ResearchAgent(docs_dir, trace_db_path=trace_db).run(task) for task in tasks]
    denied_trace = ResearchAgent(
        docs_dir,
        trace_db_path=trace_db,
        allowed_tools={"search_local_docs", "create_report", "ask_human_approval", "save_memory"},
    ).run("Extract entities from deployment strategies")
    traces.append(denied_trace)

    citation_rate = sum(1 for trace in traces if trace.citations) / len(traces)
    approval_gate_rate = sum(1 for trace in traces if trace.approval_required) / len(traces)
    unsupported_trace = next(trace for trace in traces if trace.task_intent == "unsupported")
    no_evidence_trace = next(trace for trace in traces if "quantum banana" in trace.task.lower())
    summary = {
        "task_count": len(traces),
        "traces_written": len(
            ResearchAgent(docs_dir, trace_db_path=trace_db).recent_traces(limit=20)
        ),
        "citation_rate": round(citation_rate, 3),
        "approval_gate_rate": round(approval_gate_rate, 3),
        "unsupported_task_handling": unsupported_trace.task_intent == "unsupported",
        "no_evidence_handling": not no_evidence_trace.citations,
        "tool_error_handling": all(
            call.status in {"ok", "denied", "error"}
            for trace in traces
            for call in trace.tool_calls
        ),
        "passed": True,
    }
    summary["passed"] = bool(
        summary["unsupported_task_handling"]
        and summary["no_evidence_handling"]
        and summary["tool_error_handling"]
    )

    (output_dir / "agent_eval_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    _write_report(summary, output_dir / "agent_eval_report.md")
    (output_dir / "sample_trace.json").write_text(
        traces[0].model_dump_json(indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    print(f"Wrote agent demo outputs to {output_dir}")


if __name__ == "__main__":
    main()
