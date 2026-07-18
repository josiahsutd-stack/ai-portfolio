from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

from site_robot_safety_monitor import (  # noqa: E402
    RULE_THRESHOLDS,
    analyze_telemetry,
    load_telemetry,
)


def build_summary() -> dict[str, object]:
    data_path = PROJECT_ROOT / "sample_data" / "synthetic_robot_telemetry.csv"
    data = load_telemetry(data_path)
    analysis = analyze_telemetry(data)
    events = analysis["events"]
    by_type = Counter(str(event["risk_type"]) for event in events)
    return {
        "artifact_schema_version": 1,
        "data_status": "synthetic",
        "report_type": "deterministic_rule_execution",
        "dataset": {
            "path": data_path.relative_to(REPO_ROOT).as_posix(),
            "row_count": len(data),
        },
        "thresholds": RULE_THRESHOLDS,
        "result": {
            "event_count": analysis["event_count"],
            "high_count": analysis["high_count"],
            "medium_count": analysis["medium_count"],
            "events_by_type": dict(sorted(by_type.items())),
        },
        "first_event": events[0] if events else None,
        "evaluation_boundary": (
            "Rule execution over an unlabeled synthetic fixture; no precision, recall, "
            "false-positive, or physical-safety claim."
        ),
    }


def _write_report(summary: dict[str, object], path: Path) -> None:
    dataset = summary["dataset"]
    result = summary["result"]
    first_event = summary["first_event"]
    lines = [
        "# Robot Safety Rule Execution Report",
        "",
        "Deterministic execution over bundled synthetic telemetry. This is not a safety-accuracy evaluation because the fixture has no ground-truth event labels.",
        "",
        "## Fixture Result",
        "",
        f"- Input rows: {dataset['row_count']}",
        f"- Rule events: {result['event_count']}",
        f"- High severity: {result['high_count']}",
        f"- Medium severity: {result['medium_count']}",
        "",
        "## Events By Rule",
        "",
    ]
    for risk_type, count in result["events_by_type"].items():
        lines.append(f"- {risk_type}: {count}")
    lines.extend(["", "## First Emitted Event", ""])
    if first_event:
        lines.extend(
            [
                f"- Timestamp: {first_event['timestamp']}",
                f"- Robot: {first_event['robot_id']}",
                f"- Rule: {first_event['risk_type']}",
                f"- Severity: {first_event['severity']}",
                f"- Evidence: {first_event['evidence']}",
                f"- Recommended action: {first_event['recommended_action']}",
            ]
        )
    else:
        lines.append("No event was emitted.")
    lines.extend(
        [
            "",
            "## Interpretation Boundary",
            "",
            "- All telemetry is synthetic and generated locally.",
            "- Thresholds are hand-authored demonstration values, not values derived from a robotics safety standard.",
            "- The fixture has no labeled truth set, so false positives, false negatives, precision, and recall are unknown.",
            "- No sensors, ROS messages, controller integration, latency testing, hardware, field testing, or certified safety logic are included.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    output_dir = PROJECT_ROOT / "demo_outputs"
    output_dir.mkdir(exist_ok=True)
    summary = build_summary()
    (output_dir / "safety_monitor_demo_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    _write_report(summary, output_dir / "safety_monitor_demo_report.md")
    print(json.dumps(summary["result"], indent=2))
    print(f"Wrote robot-safety demo artifacts to {output_dir}")


if __name__ == "__main__":
    main()
