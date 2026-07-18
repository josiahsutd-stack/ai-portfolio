from __future__ import annotations

from pathlib import Path

import pytest
from constraint_aware_massing_explorer import (
    OBJECTIVES,
    Mass,
    MassingCandidate,
    Rect,
    assess_candidate,
    generate_candidates,
    load_scenarios,
    rank_candidates,
    render_candidate_svg,
    run_benchmark,
    write_evaluation_artifacts,
)
from constraint_aware_massing_explorer.models import SiteScenario

ROOT = Path(__file__).resolve().parents[1]
SCENARIO_PATH = (
    ROOT
    / "experiments"
    / "constraint-aware-massing-explorer"
    / "sample_data"
    / "synthetic_site_scenarios.json"
)


@pytest.fixture(scope="module")
def scenarios() -> list[SiteScenario]:
    return load_scenarios(SCENARIO_PATH)


def test_bundled_scenarios_are_valid_and_explicitly_synthetic(
    scenarios: list[SiteScenario],
) -> None:
    assert len(scenarios) == 3
    assert len({scenario.scenario_id for scenario in scenarios}) == 3
    assert all(scenario.data_status == "synthetic" for scenario in scenarios)
    assert all(scenario.buildable_bounds.area < scenario.site_bounds.area for scenario in scenarios)


def test_scenario_rejects_missing_synthetic_label(scenarios: list[SiteScenario]) -> None:
    payload = scenarios[0].to_dict()
    payload["data_status"] = "public"

    with pytest.raises(ValueError, match="synthetic"):
        SiteScenario.from_dict(payload)


def test_generation_is_deterministic(scenarios: list[SiteScenario]) -> None:
    first = generate_candidates(scenarios[0], count=24, seed=19)
    second = generate_candidates(scenarios[0], count=24, seed=19)

    assert [candidate.to_dict() for candidate in first] == [
        candidate.to_dict() for candidate in second
    ]


def test_constraint_aware_search_returns_feasible_options(
    scenarios: list[SiteScenario],
) -> None:
    for scenario in scenarios:
        candidates = generate_candidates(scenario, count=80, seed=11)
        assessments = rank_candidates(candidates, scenario)
        feasible = [assessment for assessment in assessments if assessment.feasible]
        assert feasible
        assert all(not assessment.violations for assessment in feasible)
        assert all(
            assessment.metrics["height_m"] <= scenario.max_height_m for assessment in feasible
        )
        assert all(
            assessment.metrics["coverage"] <= scenario.max_site_coverage for assessment in feasible
        )
        assert all(assessment.metrics["gfa_m2"] <= scenario.max_gfa_m2 for assessment in feasible)


def test_validator_reports_multiple_hard_failures(scenarios: list[SiteScenario]) -> None:
    scenario = scenarios[0]
    candidate = MassingCandidate(
        candidate_id="invalid",
        typology="slab",
        generator="test",
        masses=(
            Mass(
                "A",
                Rect(-2.0, -2.0, scenario.site_width_m + 4.0, scenario.site_depth_m + 4.0),
                scenario.max_floors + 2,
            ),
        ),
    )

    assessment = assess_candidate(candidate, scenario)
    codes = {violation.code for violation in assessment.violations}

    assert not assessment.feasible
    assert {"outside_site", "setback_envelope", "height_limit", "site_coverage"} <= codes
    assert "max_gfa" in codes


def test_access_path_no_result_is_explicit(scenarios: list[SiteScenario]) -> None:
    scenario = scenarios[0]
    candidate = MassingCandidate(
        candidate_id="blocked-access",
        typology="site_block",
        generator="test",
        masses=(Mass("A", scenario.site_bounds, 1),),
    )

    assessment = assess_candidate(candidate, scenario)
    codes = {violation.code for violation in assessment.violations}

    assert assessment.metrics["ingress_path_m"] == -1.0
    assert assessment.metrics["egress_path_m"] == -1.0
    assert {"ingress_path", "egress_path"} <= codes


def test_pareto_options_are_not_dominated(scenarios: list[SiteScenario]) -> None:
    assessments = rank_candidates(
        generate_candidates(scenarios[0], count=96, seed=23), scenarios[0]
    )
    feasible = [assessment for assessment in assessments if assessment.feasible]
    front = [assessment for assessment in feasible if assessment.pareto_optimal]
    assert front
    for candidate in front:
        for other in feasible:
            if other.candidate.candidate_id == candidate.candidate.candidate_id:
                continue
            all_at_least = all(
                other.metrics[objective] >= candidate.metrics[objective] for objective in OBJECTIVES
            )
            one_better = any(
                other.metrics[objective] > candidate.metrics[objective] for objective in OBJECTIVES
            )
            assert not (all_at_least and one_better)


def test_constraint_aware_mode_beats_unconstrained_feasibility(
    scenarios: list[SiteScenario],
) -> None:
    summary, _selected = run_benchmark(scenarios, candidate_count=48, seeds=(5, 13))
    aggregate = summary["aggregate"]

    assert aggregate["constraint_aware_feasible_rate"] > aggregate["baseline_feasible_rate"]
    assert (
        aggregate["constraint_aware_mean_best_utility"] >= aggregate["baseline_mean_best_utility"]
    )


def test_svg_is_derived_from_selected_candidate(scenarios: list[SiteScenario]) -> None:
    scenario = scenarios[0]
    assessment = next(
        item
        for item in rank_candidates(generate_candidates(scenario, count=64, seed=11), scenario)
        if item.feasible
    )

    svg = render_candidate_svg(scenario, assessment)

    assert svg.startswith("<svg")
    assert "SYNTHETIC SCENARIO" in svg
    assert assessment.candidate.candidate_id in svg
    assert scenario.name in svg
    assert "not code certification" in svg.lower()


def test_evaluation_artifacts_are_deterministic(
    tmp_path: Path, scenarios: list[SiteScenario]
) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    write_evaluation_artifacts(scenarios, first, candidate_count=32, seeds=(7,))
    write_evaluation_artifacts(scenarios, second, candidate_count=32, seeds=(7,))

    first_files = sorted(path.name for path in first.iterdir())
    second_files = sorted(path.name for path in second.iterdir())
    assert first_files == second_files
    for name in first_files:
        assert (first / name).read_bytes() == (second / name).read_bytes()
