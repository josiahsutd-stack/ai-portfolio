from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .costing import build_cost_estimate
from .models import FloorPlan, RateLibrary, TenderSubmission
from .rendering import (
    render_cost_breakdown_svg,
    render_floor_plan_svg,
    render_tender_comparison_svg,
)
from .takeoff import calculate_takeoff, naive_room_perimeter_length_m
from .tender import analyze_tender, review_flags


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_floor_plans(path: str | Path) -> list[FloorPlan]:
    payload = load_json(path)
    if payload.get("data_status") != "synthetic":
        raise ValueError("Floor-plan fixture collection must be labeled synthetic.")
    return [FloorPlan.from_dict(item) for item in payload["plans"]]


def load_rate_library(path: str | Path) -> RateLibrary:
    return RateLibrary.from_dict(load_json(path))


def load_tenders(path: str | Path) -> tuple[str, list[TenderSubmission]]:
    payload = load_json(path)
    if payload.get("data_status") != "synthetic":
        raise ValueError("Tender fixture collection must be labeled synthetic.")
    return str(payload["benchmark_plan_id"]), [
        TenderSubmission.from_dict(item) for item in payload["tenders"]
    ]


def _precision_recall_f1(
    predicted: set[tuple[str, str, str]], expected: set[tuple[str, str, str]]
) -> dict[str, float]:
    true_positive = len(predicted & expected)
    precision = true_positive / len(predicted) if predicted else float(not expected)
    recall = true_positive / len(expected) if expected else float(not predicted)
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": round(precision, 6), "recall": round(recall, 6), "f1": round(f1, 6)}


def evaluate_qs_workflow(
    plans: list[FloorPlan],
    rate_library: RateLibrary,
    evaluation_cases: dict[str, Any],
    benchmark_plan_id: str,
    tenders: list[TenderSubmission],
) -> dict[str, Any]:
    expected_by_plan = {case["plan_id"]: case for case in evaluation_cases["takeoff_cases"]}
    plan_results: list[dict[str, Any]] = []
    quantity_abs_errors: list[float] = []
    wall_errors: list[float] = []
    baseline_wall_errors: list[float] = []
    cost_abs_errors: list[float] = []
    provenance_lines = 0
    priced_lines = 0
    computed: dict[str, tuple[Any, Any]] = {}

    for plan in plans:
        expected = expected_by_plan[plan.plan_id]
        takeoff = calculate_takeoff(plan)
        estimate = build_cost_estimate(takeoff, rate_library)
        computed[plan.plan_id] = (takeoff, estimate)
        quantities = takeoff.quantity_map()
        expected_quantities = expected["expected_quantities"]
        for code, expected_value in expected_quantities.items():
            quantity_abs_errors.append(abs(quantities[code] - float(expected_value)))
        expected_wall_total = float(expected["external_wall_length_m"]) + float(
            expected["partition_length_m"]
        )
        measured_wall_total = takeoff.external_wall_length_m + takeoff.partition_length_m
        wall_errors.append(abs(measured_wall_total - expected_wall_total))
        baseline_wall_errors.append(abs(naive_room_perimeter_length_m(plan) - expected_wall_total))
        cost_abs_errors.append(abs(estimate.base_total - float(expected["expected_cost_total"])))
        priced_lines += len(estimate.priced_lines)
        provenance_lines += sum(
            bool(line.rate_provenance and line.quantity_source_refs)
            for line in estimate.priced_lines
        )
        plan_results.append(
            {
                "plan_id": plan.plan_id,
                "quantity_line_count": len(quantities),
                "max_quantity_abs_error": round(
                    max(
                        abs(quantities[code] - float(value))
                        for code, value in expected_quantities.items()
                    ),
                    6,
                ),
                "wall_length_abs_error_m": round(abs(measured_wall_total - expected_wall_total), 6),
                "naive_perimeter_wall_abs_error_m": round(
                    abs(naive_room_perimeter_length_m(plan) - expected_wall_total), 6
                ),
                "cost_abs_error": round(
                    abs(estimate.base_total - float(expected["expected_cost_total"])), 6
                ),
            }
        )

    benchmark_takeoff, benchmark_estimate = computed[benchmark_plan_id]
    analyses = [analyze_tender(tender, benchmark_estimate) for tender in tenders]
    predicted_flags = {
        (analysis.tender_id, flag.item_code, flag.flag)
        for analysis in analyses
        for flag in review_flags(analysis)
    }
    expected_flags = {
        (str(item["tender_id"]), str(item["item_code"]), str(item["flag"]))
        for item in evaluation_cases["expected_tender_flags"]
    }
    flag_metrics = _precision_recall_f1(predicted_flags, expected_flags)
    quantity_exact = sum(error <= 1e-6 for error in quantity_abs_errors)

    return {
        "scope": {
            "data_status": "synthetic",
            "plan_count": len(plans),
            "quantity_line_count": len(quantity_abs_errors),
            "tender_count": len(tenders),
            "evaluation_note": "Authored deterministic fixture regression; not arbitrary drawing understanding or market-price validation.",
        },
        "metrics": {
            "quantity_line_exact_match_rate": round(quantity_exact / len(quantity_abs_errors), 6),
            "quantity_mean_absolute_error": round(
                sum(quantity_abs_errors) / len(quantity_abs_errors), 6
            ),
            "wall_length_mean_absolute_error_m": round(sum(wall_errors) / len(wall_errors), 6),
            "naive_perimeter_wall_mean_absolute_error_m": round(
                sum(baseline_wall_errors) / len(baseline_wall_errors), 6
            ),
            "cost_total_mean_absolute_error": round(sum(cost_abs_errors) / len(cost_abs_errors), 6),
            "cost_line_provenance_coverage": round(provenance_lines / priced_lines, 6),
            "tender_flag_precision": flag_metrics["precision"],
            "tender_flag_recall": flag_metrics["recall"],
            "tender_flag_f1": flag_metrics["f1"],
        },
        "plan_results": plan_results,
        "tender_results": [analysis.to_dict() for analysis in analyses],
        "fixture_mismatches": {
            "unexpected_tender_flags": sorted(predicted_flags - expected_flags),
            "missed_tender_flags": sorted(expected_flags - predicted_flags),
        },
        "sample": {
            "plan_id": benchmark_plan_id,
            "takeoff": benchmark_takeoff.to_dict(),
            "estimate": benchmark_estimate.to_dict(),
        },
    }


def write_evaluation_artifacts(
    project_root: str | Path,
    output_dir: str | Path,
) -> dict[str, Any]:
    project_root = Path(project_root)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    plans = load_floor_plans(project_root / "sample_data" / "synthetic_floor_plans.json")
    rates = load_rate_library(project_root / "sample_data" / "synthetic_rate_library.json")
    benchmark_plan_id, tenders = load_tenders(
        project_root / "sample_data" / "synthetic_tenders.json"
    )
    cases = load_json(project_root / "sample_data" / "evaluation_cases.json")
    summary = evaluate_qs_workflow(plans, rates, cases, benchmark_plan_id, tenders)

    (output_dir / "evaluation_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    metrics = summary["metrics"]
    report = "\n".join(
        [
            "# QS Workflow Evaluation",
            "",
            "**Data status:** synthetic vector plans, synthetic unit rates, and synthetic anonymous tenders.",
            "",
            "| Metric | Result |",
            "| --- | ---: |",
            *[f"| {key.replace('_', ' ').title()} | {value} |" for key, value in metrics.items()],
            "",
            "The exact fixture scores test deterministic regressions over authored rectangular plans. They do not establish performance on PDF drawings, CAD/BIM files, real rate books, or live tenders.",
            "",
        ]
    )
    (output_dir / "evaluation_report.md").write_text(report, encoding="utf-8")
    mismatches = summary["fixture_mismatches"]
    failure_report = "\n".join(
        [
            "# Failure Analysis",
            "",
            f"- Unexpected tender flags: {mismatches['unexpected_tender_flags'] or 'none'}",
            f"- Missed tender flags: {mismatches['missed_tender_flags'] or 'none'}",
            "- Unsupported inputs fail closed when scale is missing, rooms overlap, openings leave a wall, or units conflict.",
            "- Remaining real-world failure modes are documented in `../LIMITATIONS.md`.",
            "",
        ]
    )
    (output_dir / "failure_analysis.md").write_text(failure_report, encoding="utf-8")

    sample_plan = next(plan for plan in plans if plan.plan_id == benchmark_plan_id)
    sample_takeoff, sample_estimate = (
        calculate_takeoff(sample_plan),
        build_cost_estimate(calculate_takeoff(sample_plan), rates),
    )
    sample_analyses = [analyze_tender(tender, sample_estimate) for tender in tenders]
    (output_dir / "sample_estimate.json").write_text(
        json.dumps(sample_estimate.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "sample_tender_analysis.json").write_text(
        json.dumps([analysis.to_dict() for analysis in sample_analyses], indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    with (output_dir / "sample_takeoff.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["item_code", "description", "unit", "quantity", "formula", "source_refs"],
        )
        writer.writeheader()
        for line in sample_takeoff.quantities:
            row = line.to_dict()
            row["source_refs"] = "|".join(line.source_refs)
            writer.writerow(row)
    (output_dir / "sample_plan.svg").write_text(
        render_floor_plan_svg(sample_plan, sample_takeoff), encoding="utf-8"
    )
    (output_dir / "cost_breakdown.svg").write_text(
        render_cost_breakdown_svg(sample_estimate), encoding="utf-8"
    )
    (output_dir / "tender_comparison.svg").write_text(
        render_tender_comparison_svg(sample_analyses), encoding="utf-8"
    )
    return summary
