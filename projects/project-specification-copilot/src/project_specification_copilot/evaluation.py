from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .engine import SpecificationEngine
from .rendering import render_specification_trace_svg


def load_evaluation_cases(path: str | Path) -> list[dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Evaluation file must contain a JSON list.")
    case_ids = [str(case["case_id"]) for case in payload]
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("Evaluation case ids must be unique.")
    return [dict(case) for case in payload]


def _f1(true_positive: int, predicted: int, expected: int) -> tuple[float, float, float]:
    precision = true_positive / predicted if predicted else (1.0 if expected == 0 else 0.0)
    recall = true_positive / expected if expected else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return round(precision, 6), round(recall, 6), round(f1, 6)


def evaluate_cases(cases: list[dict[str, Any]]) -> tuple[dict[str, Any], list[SpecificationEngine]]:
    extraction_tp = extraction_predicted = extraction_expected = 0
    conflict_tp = conflict_predicted = conflict_expected = 0
    approval_tp = approval_predicted = approval_expected = 0
    clause_tp = clause_predicted = clause_expected = 0
    cited_requirements = total_requirements = 0
    denied_expected = denied_observed = 0
    status_correct = 0
    engines: list[SpecificationEngine] = []
    case_results: list[dict[str, Any]] = []

    for case in cases:
        engine = SpecificationEngine()
        for row in case["messages"]:
            engine.submit_message(
                role=str(row["role"]),
                author=str(row.get("author", row["role"])),
                text=str(row["text"]),
                data_status="synthetic",
            )
        snapshot = engine.snapshot()
        draft = engine.draft_specification()
        engines.append(engine)

        active = {
            (requirement.key, str(requirement.value).lower())
            for requirement in snapshot.requirements
            if requirement.status in {"proposed", "approved"}
        }
        expected_active = {
            (str(item["key"]), str(item["value"]).lower())
            for item in case["expected_active_requirements"]
        }
        predicted_conflicts = {
            conflict.requirement_key for conflict in snapshot.conflicts if conflict.status == "open"
        }
        expected_conflicts = set(case["expected_open_conflict_keys"])
        predicted_approved = {
            requirement.key
            for requirement in snapshot.requirements
            if requirement.status == "approved"
        }
        expected_approved = set(case["expected_approved_keys"])
        predicted_clause_ids = {clause.requirement_id for clause in draft.clauses}
        expected_clause_keys = set(case["expected_spec_clause_keys"])
        predicted_clause_keys = {
            requirement.key
            for requirement in snapshot.requirements
            if requirement.requirement_id in predicted_clause_ids
        }

        extraction_tp += len(active & expected_active)
        extraction_predicted += len(active)
        extraction_expected += len(expected_active)
        conflict_tp += len(predicted_conflicts & expected_conflicts)
        conflict_predicted += len(predicted_conflicts)
        conflict_expected += len(expected_conflicts)
        approval_tp += len(predicted_approved & expected_approved)
        approval_predicted += len(predicted_approved)
        approval_expected += len(expected_approved)
        clause_tp += len(predicted_clause_keys & expected_clause_keys)
        clause_predicted += len(predicted_clause_keys)
        clause_expected += len(expected_clause_keys)
        total_requirements += len(snapshot.requirements)
        cited_requirements += sum(
            bool(requirement.source_message_ids) for requirement in snapshot.requirements
        )
        denied_expected += int(case.get("expected_denied_approvals", 0))
        denied_observed += snapshot.denied_approval_count
        expected_status = str(case.get("expected_draft_status", "draft_for_review"))
        status_correct += int(draft.status == expected_status)
        case_results.append(
            {
                "case_id": case["case_id"],
                "active_requirement_pairs": sorted([list(item) for item in active]),
                "open_conflict_keys": sorted(predicted_conflicts),
                "approved_keys": sorted(predicted_approved),
                "spec_clause_keys": sorted(predicted_clause_keys),
                "denied_approval_count": snapshot.denied_approval_count,
                "draft_status": draft.status,
            }
        )

    extraction = _f1(extraction_tp, extraction_predicted, extraction_expected)
    conflicts = _f1(conflict_tp, conflict_predicted, conflict_expected)
    approvals = _f1(approval_tp, approval_predicted, approval_expected)
    clauses = _f1(clause_tp, clause_predicted, clause_expected)
    summary = {
        "artifact_schema_version": 1,
        "data_status": "synthetic",
        "case_count": len(cases),
        "message_count": sum(len(case["messages"]) for case in cases),
        "metrics": {
            "requirement_extraction_precision": extraction[0],
            "requirement_extraction_recall": extraction[1],
            "requirement_extraction_f1": extraction[2],
            "open_conflict_precision": conflicts[0],
            "open_conflict_recall": conflicts[1],
            "open_conflict_f1": conflicts[2],
            "approval_state_precision": approvals[0],
            "approval_state_recall": approvals[1],
            "approval_state_f1": approvals[2],
            "spec_clause_precision": clauses[0],
            "spec_clause_recall": clauses[1],
            "spec_clause_f1": clauses[2],
            "requirement_citation_coverage": round(
                cited_requirements / total_requirements if total_requirements else 1.0, 6
            ),
            "denied_approval_count_accuracy": round(
                1.0 - abs(denied_observed - denied_expected) / max(1, denied_expected), 6
            ),
            "draft_status_accuracy": round(status_correct / len(cases), 6),
        },
        "expected_denied_approvals": denied_expected,
        "observed_denied_approvals": denied_observed,
        "case_results": case_results,
        "boundaries": [
            "Rule-based extraction over a documented phrase set; not open-domain language understanding.",
            "Evaluation conversations and labels are synthetic and authored for this repository.",
            "Specification clauses require recorded role-authorized approval and remain drafts for professional review.",
        ],
    }
    return summary, engines


def write_evaluation_artifacts(
    cases: list[dict[str, Any]], output_dir: str | Path
) -> dict[str, Any]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    summary, engines = evaluate_cases(cases)
    (output / "evaluation_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    metrics = summary["metrics"]
    report = f"""# Project Communication and Specification Assistant Evaluation

**Data status:** synthetic

The checked-in benchmark contains {summary['case_count']} synthetic conversations and {summary['message_count']} role-tagged messages.

| Metric | Result |
| --- | ---: |
| Requirement extraction F1 | {metrics['requirement_extraction_f1']:.3f} |
| Open-conflict F1 | {metrics['open_conflict_f1']:.3f} |
| Approval-state F1 | {metrics['approval_state_f1']:.3f} |
| Specification-clause F1 | {metrics['spec_clause_f1']:.3f} |
| Requirement citation coverage | {metrics['requirement_citation_coverage']:.3f} |
| Draft-status accuracy | {metrics['draft_status_accuracy']:.3f} |

These results measure a documented deterministic phrase set and role matrix over repository-authored fixtures. They are not evidence of open-domain conversation understanding or professional specification quality.
"""
    (output / "evaluation_report.md").write_text(report, encoding="utf-8")
    failures: list[str] = []
    for case, result in zip(cases, summary["case_results"], strict=True):
        expected_pairs = sorted(
            [
                [str(item["key"]), str(item["value"]).lower()]
                for item in case["expected_active_requirements"]
            ]
        )
        comparisons = {
            "active requirements": (expected_pairs, result["active_requirement_pairs"]),
            "open conflicts": (
                sorted(case["expected_open_conflict_keys"]),
                result["open_conflict_keys"],
            ),
            "approved keys": (sorted(case["expected_approved_keys"]), result["approved_keys"]),
            "spec clause keys": (
                sorted(case["expected_spec_clause_keys"]),
                result["spec_clause_keys"],
            ),
        }
        for label, (expected, observed) in comparisons.items():
            if expected != observed:
                failures.append(
                    f"- `{case['case_id']}` {label}: expected `{expected}`, observed `{observed}`."
                )
    failure_text = "\n".join(failures) if failures else "No fixture-level mismatches were recorded."
    (output / "failure_analysis.md").write_text(
        "# Failure Analysis\n\n**Data status:** synthetic\n\n"
        + failure_text
        + "\n\nThe absence of fixture mismatches would show regression consistency only; it would not establish general language coverage.\n",
        encoding="utf-8",
    )
    first = engines[0]
    first_draft = first.draft_specification()
    (output / "sample_specification.md").write_text(first_draft.markdown, encoding="utf-8")
    (output / "sample_trace.svg").write_text(
        render_specification_trace_svg(first.snapshot(), first_draft), encoding="utf-8"
    )
    (output / "sample_audit_trace.json").write_text(
        json.dumps(
            [
                {
                    "event_id": event.event_id,
                    "event_type": event.event_type,
                    "payload": event.payload,
                }
                for event in first.store.events()
            ],
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return summary
