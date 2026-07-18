from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any

from .assessment import rank_candidates
from .generation import generate_candidates
from .models import CandidateAssessment, SiteScenario
from .rendering import render_candidate_svg, render_comparison_svg


def load_scenarios(path: str | Path) -> list[SiteScenario]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Scenario file must contain a JSON list.")
    scenarios = [SiteScenario.from_dict(dict(row)) for row in payload]
    scenario_ids = [scenario.scenario_id for scenario in scenarios]
    if len(scenario_ids) != len(set(scenario_ids)):
        raise ValueError("Scenario ids must be unique.")
    return scenarios


def _mode_metrics(assessments: list[CandidateAssessment]) -> dict[str, Any]:
    feasible = [assessment for assessment in assessments if assessment.feasible]
    pareto = [assessment for assessment in feasible if assessment.pareto_optimal]
    violation_counts = Counter(
        violation.code for assessment in assessments for violation in assessment.violations
    )
    return {
        "candidate_count": len(assessments),
        "feasible_count": len(feasible),
        "feasible_rate": round(len(feasible) / len(assessments), 6),
        "pareto_count": len(pareto),
        "best_utility": round(max((item.utility_score for item in feasible), default=0.0), 6),
        "best_gfa_error_fraction": round(
            min((item.metrics["gfa_error_fraction"] for item in feasible), default=1.0), 6
        ),
        "violation_counts": dict(sorted(violation_counts.items())),
    }


def run_benchmark(
    scenarios: list[SiteScenario],
    candidate_count: int = 96,
    seeds: tuple[int, ...] = (11, 23, 37),
) -> tuple[dict[str, Any], dict[str, list[CandidateAssessment]]]:
    runs: list[dict[str, Any]] = []
    selected: dict[str, list[CandidateAssessment]] = {}
    for scenario in scenarios:
        for seed in seeds:
            mode_results: dict[str, Any] = {}
            for mode in ("unconstrained_baseline", "constraint_aware"):
                candidates = generate_candidates(
                    scenario, count=candidate_count, seed=seed, mode=mode
                )
                assessments = rank_candidates(candidates, scenario)
                mode_results[mode] = _mode_metrics(assessments)
                if mode == "constraint_aware" and seed == seeds[0]:
                    selected[scenario.scenario_id] = [
                        assessment
                        for assessment in assessments
                        if assessment.feasible and assessment.pareto_optimal
                    ][:6]
            runs.append(
                {
                    "scenario_id": scenario.scenario_id,
                    "seed": seed,
                    "modes": mode_results,
                }
            )

    constrained = [run["modes"]["constraint_aware"] for run in runs]
    baseline = [run["modes"]["unconstrained_baseline"] for run in runs]
    summary = {
        "artifact_schema_version": 1,
        "data_status": "synthetic",
        "evaluation_scope": "fixed bundled synthetic sites and deterministic seeded search",
        "scenario_count": len(scenarios),
        "candidate_count_per_mode_per_run": candidate_count,
        "seeds": list(seeds),
        "run_count": len(runs),
        "aggregate": {
            "constraint_aware_feasible_rate": round(
                mean(item["feasible_rate"] for item in constrained), 6
            ),
            "baseline_feasible_rate": round(mean(item["feasible_rate"] for item in baseline), 6),
            "constraint_aware_mean_best_utility": round(
                mean(item["best_utility"] for item in constrained), 6
            ),
            "baseline_mean_best_utility": round(mean(item["best_utility"] for item in baseline), 6),
            "constraint_aware_mean_best_gfa_error_fraction": round(
                mean(item["best_gfa_error_fraction"] for item in constrained), 6
            ),
            "baseline_mean_best_gfa_error_fraction": round(
                mean(item["best_gfa_error_fraction"] for item in baseline), 6
            ),
        },
        "runs": runs,
        "boundaries": [
            "No rule inference from building codes; all numeric constraints are supplied inputs.",
            "Solar, daylight, wind, and access values are transparent geometric proxies.",
            "The access grid covers open-site routes only, not internal egress compliance.",
            "No CFD, climate model, daylight engine, structure, cost, or constructability analysis.",
        ],
    }
    return summary, selected


def _evaluation_report(summary: dict[str, Any]) -> str:
    aggregate = summary["aggregate"]
    return f"""# Massing Search Evaluation

**Data status:** synthetic

The benchmark uses {summary['scenario_count']} bundled synthetic sites, {summary['candidate_count_per_mode_per_run']} candidates per mode, and fixed seeds `{summary['seeds']}`. It compares geometry sampled without constraint awareness against the constraint-aware generator using the same validator and objective calculations.

| Metric | Constraint-aware | Unconstrained baseline |
| --- | ---: | ---: |
| Mean feasible-candidate rate | {aggregate['constraint_aware_feasible_rate']:.3f} | {aggregate['baseline_feasible_rate']:.3f} |
| Mean best utility per run | {aggregate['constraint_aware_mean_best_utility']:.3f} | {aggregate['baseline_mean_best_utility']:.3f} |
| Mean best GFA error | {aggregate['constraint_aware_mean_best_gfa_error_fraction'] * 100:.2f}% | {aggregate['baseline_mean_best_gfa_error_fraction'] * 100:.2f}% |

Feasibility means the candidate passed the supplied site, setback, height, site-coverage, maximum-GFA, overlap, and open-site access-path checks. Utility is a transparent weighted score over target-GFA fit and four proxy objectives. These numbers are regression evidence for this local search implementation, not architectural performance or regulatory validation.
"""


def _failure_report(summary: dict[str, Any]) -> str:
    counters: dict[str, Counter[str]] = {
        "constraint_aware": Counter(),
        "unconstrained_baseline": Counter(),
    }
    for run in summary["runs"]:
        for mode in counters:
            counters[mode].update(run["modes"][mode]["violation_counts"])
    rows = []
    codes = sorted(set(counters["constraint_aware"]) | set(counters["unconstrained_baseline"]))
    for code in codes:
        rows.append(
            f"| `{code}` | {counters['constraint_aware'][code]} | {counters['unconstrained_baseline'][code]} |"
        )
    table = "\n".join(rows) if rows else "| none | 0 | 0 |"
    return f"""# Failure Analysis

**Data status:** synthetic

Violation counts are event counts, so one candidate may contribute more than one violation.

| Validator code | Constraint-aware | Unconstrained baseline |
| --- | ---: | ---: |
{table}

The generator does not repair every invalid option. Invalid candidates remain visible in the evaluation so that feasibility yield and recurrent failure modes can be inspected.
"""


def write_evaluation_artifacts(
    scenarios: list[SiteScenario],
    output_dir: str | Path,
    candidate_count: int = 96,
    seeds: tuple[int, ...] = (11, 23, 37),
) -> dict[str, Any]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    summary, selected = run_benchmark(scenarios, candidate_count=candidate_count, seeds=seeds)
    (output / "evaluation_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output / "evaluation_report.md").write_text(_evaluation_report(summary), encoding="utf-8")
    (output / "failure_analysis.md").write_text(_failure_report(summary), encoding="utf-8")
    option_payload: dict[str, Any] = {"data_status": "synthetic", "scenarios": {}}
    for scenario in scenarios:
        options = selected.get(scenario.scenario_id, [])
        option_payload["scenarios"][scenario.scenario_id] = [item.to_dict() for item in options]
    (output / "top_options.json").write_text(
        json.dumps(option_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    first_scenario = scenarios[0]
    first_options = selected[first_scenario.scenario_id]
    if not first_options:
        raise RuntimeError("Evaluation produced no feasible Pareto option for the first scenario.")
    (output / "top_option.svg").write_text(
        render_candidate_svg(first_scenario, first_options[0]), encoding="utf-8"
    )
    (output / "option_comparison.svg").write_text(
        render_comparison_svg(first_scenario, first_options[:3]), encoding="utf-8"
    )
    return summary
