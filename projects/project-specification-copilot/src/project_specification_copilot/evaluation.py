from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .engine import SpecificationEngine
from .extractor import extract_requirements
from .models import Message
from .rendering import render_specification_trace_svg

LANGUAGE_STRESS_GROUPS = ("direct_form", "paraphrase", "negative_control")


def load_evaluation_cases(path: str | Path) -> list[dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Evaluation file must contain a JSON list.")
    case_ids = [str(case["case_id"]) for case in payload]
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("Evaluation case ids must be unique.")
    return [dict(case) for case in payload]


def load_language_stress_cases(
    path: str | Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("cases"), list):
        raise ValueError("Language stress file must contain an object with a `cases` list.")
    metadata = {
        "schema_version": int(payload.get("schema_version", 1)),
        "data_status": str(payload.get("data_status", "synthetic")),
        "label_source": str(payload.get("label_source", "")),
        "evaluation_scope": str(payload.get("evaluation_scope", "")),
    }
    if metadata["data_status"] != "synthetic":
        raise ValueError("Language stress data must remain explicitly labeled synthetic.")
    if not metadata["label_source"]:
        raise ValueError("Language stress data requires a label_source.")
    cases = [dict(case) for case in payload["cases"]]
    case_ids = [str(case.get("case_id", "")) for case in cases]
    if not all(case_ids) or len(case_ids) != len(set(case_ids)):
        raise ValueError("Language stress case ids must be present and unique.")
    for case in cases:
        if case.get("group") not in LANGUAGE_STRESS_GROUPS:
            raise ValueError(f"Unsupported language stress group: {case.get('group')}")
        if not str(case.get("text", "")).strip():
            raise ValueError(f"Language stress case {case['case_id']} has no text.")
        if not isinstance(case.get("expected_requirements"), list):
            raise ValueError(
                f"Language stress case {case['case_id']} requires expected_requirements."
            )
    return metadata, cases


def _f1(true_positive: int, predicted: int, expected: int) -> tuple[float, float, float]:
    precision = true_positive / predicted if predicted else (1.0 if expected == 0 else 0.0)
    recall = true_positive / expected if expected else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return round(precision, 6), round(recall, 6), round(f1, 6)


def _requirement_pairs(items: list[dict[str, Any]]) -> set[tuple[str, str]]:
    return {(str(item["key"]), str(item["value"]).strip().lower()) for item in items}


def evaluate_language_stress_cases(
    cases: list[dict[str, Any]], metadata: dict[str, Any]
) -> dict[str, Any]:
    group_counts = {
        group: {"true_positive": 0, "predicted": 0, "expected": 0, "exact": 0, "count": 0}
        for group in LANGUAGE_STRESS_GROUPS
    }
    total_true_positive = total_predicted = total_expected = exact_cases = 0
    negative_case_count = clean_negative_count = 0
    case_results: list[dict[str, Any]] = []

    for index, case in enumerate(cases, start=1):
        message = Message(
            message_id=f"STRESS-{index:03d}",
            sequence=index,
            role=str(case.get("role", "client")),
            author="Synthetic participant",
            text=str(case["text"]),
            data_status="synthetic",
        )
        predicted = {
            (item.key, str(item.value).strip().lower()) for item in extract_requirements(message)
        }
        expected = _requirement_pairs(case["expected_requirements"])
        group = str(case["group"])
        true_positive = len(predicted & expected)
        exact = predicted == expected

        total_true_positive += true_positive
        total_predicted += len(predicted)
        total_expected += len(expected)
        exact_cases += int(exact)
        group_counts[group]["true_positive"] += true_positive
        group_counts[group]["predicted"] += len(predicted)
        group_counts[group]["expected"] += len(expected)
        group_counts[group]["exact"] += int(exact)
        group_counts[group]["count"] += 1
        if not expected:
            negative_case_count += 1
            clean_negative_count += int(not predicted)

        case_results.append(
            {
                "case_id": case["case_id"],
                "group": group,
                "text": case["text"],
                "expected_requirements": sorted([list(item) for item in expected]),
                "predicted_requirements": sorted([list(item) for item in predicted]),
                "missing_requirements": sorted([list(item) for item in expected - predicted]),
                "unexpected_requirements": sorted([list(item) for item in predicted - expected]),
                "exact_match": exact,
            }
        )

    precision, recall, f1 = _f1(total_true_positive, total_predicted, total_expected)
    group_metrics: dict[str, dict[str, Any]] = {}
    for group, counts in group_counts.items():
        group_precision, group_recall, group_f1 = _f1(
            counts["true_positive"], counts["predicted"], counts["expected"]
        )
        group_metrics[group] = {
            "case_count": counts["count"],
            "precision": group_precision,
            "recall": group_recall,
            "f1": group_f1,
            "exact_case_accuracy": round(counts["exact"] / counts["count"], 6),
        }

    return {
        "artifact_schema_version": 1,
        "data_status": metadata["data_status"],
        "label_source": metadata["label_source"],
        "evaluation_scope": metadata["evaluation_scope"],
        "case_count": len(cases),
        "positive_case_count": sum(bool(case["expected_requirements"]) for case in cases),
        "negative_control_case_count": negative_case_count,
        "metrics": {
            "requirement_precision": precision,
            "requirement_recall": recall,
            "requirement_f1": f1,
            "exact_case_accuracy": round(exact_cases / len(cases), 6),
            "negative_control_accuracy": round(
                clean_negative_count / negative_case_count if negative_case_count else 1.0, 6
            ),
        },
        "group_metrics": group_metrics,
        "failure_count": len(cases) - exact_cases,
        "case_results": case_results,
        "boundaries": [
            "Cases and labels are candidate-authored and are not blinded or independently validated.",
            "The set measures documented single-message forms, not open-domain conversation understanding.",
            "No result establishes professional specification quality or stakeholder acceptance.",
        ],
    }


def _language_stress_svg(summary: dict[str, Any]) -> str:
    labels = {
        "direct_form": "Direct forms",
        "paraphrase": "Paraphrases",
        "negative_control": "Negative controls",
    }
    colors = {
        "direct_form": "#167d6d",
        "paraphrase": "#e85d3f",
        "negative_control": "#d6a226",
    }
    rows: list[str] = []
    for row_index, group in enumerate(LANGUAGE_STRESS_GROUPS):
        metric = summary["group_metrics"][group]["exact_case_accuracy"]
        y = 170 + row_index * 92
        width = round(500 * metric, 1)
        rows.extend(
            [
                f'<text x="56" y="{y + 8}" font-family="Arial, sans-serif" font-size="16" font-weight="700" fill="#17231f">{labels[group]}</text>',
                f'<rect x="250" y="{y - 18}" width="500" height="34" rx="4" fill="#e7ece9"/>',
                f'<rect x="250" y="{y - 18}" width="{width}" height="34" rx="4" fill="{colors[group]}"/>',
                f'<text x="770" y="{y + 8}" font-family="Arial, sans-serif" font-size="18" font-weight="700" fill="#17231f">{metric:.3f}</text>',
            ]
        )
    metrics = summary["metrics"]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="860" height="500" viewBox="0 0 860 500" role="img" aria-labelledby="title desc">
  <title id="title">Language stress exact-case accuracy</title>
  <desc id="desc">Exact-case accuracy for direct forms, paraphrases, and negative controls in a candidate-authored synthetic stress set.</desc>
  <rect width="860" height="500" fill="#f7f8f6"/>
  <text x="56" y="48" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#e85d3f">LANGUAGE COVERAGE STRESS AUDIT · SYNTHETIC</text>
  <text x="56" y="86" font-family="Arial, sans-serif" font-size="28" font-weight="700" fill="#17231f">Exact-case accuracy by wording group</text>
  <text x="56" y="116" font-family="Arial, sans-serif" font-size="14" fill="#58645f">{summary['case_count']} candidate-authored cases · not blinded or independently labeled</text>
  {''.join(rows)}
  <line x1="56" y1="438" x2="804" y2="438" stroke="#c9d1cd"/>
  <text x="56" y="470" font-family="Arial, sans-serif" font-size="14" fill="#17231f">Overall extraction F1 {metrics['requirement_f1']:.3f} · Negative-control accuracy {metrics['negative_control_accuracy']:.3f} · {summary['failure_count']} exact-case misses retained</text>
</svg>
"""


def write_language_stress_artifacts(
    cases: list[dict[str, Any]], metadata: dict[str, Any], output_dir: str | Path
) -> dict[str, Any]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    summary = evaluate_language_stress_cases(cases, metadata)
    (output / "language_stress_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    rows = []
    for group in LANGUAGE_STRESS_GROUPS:
        metric = summary["group_metrics"][group]
        rows.append(
            f"| {group.replace('_', ' ').title()} | {metric['case_count']} | "
            f"{metric['precision']:.3f} | {metric['recall']:.3f} | {metric['f1']:.3f} | "
            f"{metric['exact_case_accuracy']:.3f} |"
        )
    metrics = summary["metrics"]
    report = f"""# Language Coverage Stress Audit

**Data status:** synthetic

**Label source:** candidate-authored, not blinded or independently validated

The fixed set contains {summary['case_count']} single-message cases: {summary['positive_case_count']} positive requirement forms and {summary['negative_control_case_count']} negative controls.

| Group | Cases | Precision | Recall | F1 | Exact-case accuracy |
| --- | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(rows)}

Overall requirement extraction F1 is `{metrics['requirement_f1']:.3f}`; exact-case accuracy is `{metrics['exact_case_accuracy']:.3f}`; negative-control accuracy is `{metrics['negative_control_accuracy']:.3f}`.

This is a repository-authored coverage audit over documented forms. It is not evidence of open-domain conversation understanding, expert agreement, or professional specification quality.
"""
    (output / "language_stress_report.md").write_text(report, encoding="utf-8")
    failures = [result for result in summary["case_results"] if not result["exact_match"]]
    failure_lines = [
        f"- `{result['case_id']}`: missing `{result['missing_requirements']}`; unexpected `{result['unexpected_requirements']}`. Text: {result['text']}"
        for result in failures
    ]
    (output / "language_stress_failures.md").write_text(
        "# Language Stress Failures\n\n**Data status:** synthetic\n\n"
        + ("\n".join(failure_lines) if failure_lines else "No exact-case misses were recorded.")
        + "\n\nThese misses are retained to bound the documented language coverage.\n",
        encoding="utf-8",
    )
    (output / "language_stress_comparison.svg").write_text(
        _language_stress_svg(summary), encoding="utf-8"
    )
    return summary


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
