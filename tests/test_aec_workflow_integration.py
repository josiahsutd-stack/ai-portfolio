from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest
from qs_takeoff_tender_analysis import RateLibrary

from shared.aec_workflow import (
    WorkflowInputError,
    load_json,
    run_aec_design_to_cost_workflow,
    write_workflow_artifacts,
)

ROOT = Path(__file__).resolve().parents[1]
CASE_PATH = (
    ROOT / "integrations" / "aec-design-to-cost" / "sample_data" / "synthetic_workflow_case.json"
)
RATE_PATH = (
    ROOT / "projects" / "qs-takeoff-tender-analysis" / "sample_data" / "synthetic_rate_library.json"
)


def workflow_case() -> dict:
    return load_json(CASE_PATH)


def rate_library() -> RateLibrary:
    return RateLibrary.from_dict(load_json(RATE_PATH))


def run_case(case: dict | None = None) -> dict:
    return run_aec_design_to_cost_workflow(case or workflow_case(), rate_library())


def test_happy_path_records_sourced_bounded_handoffs() -> None:
    trace = run_case()

    specification = trace["specification_handoff"]
    assert specification["approved_requirement_count"] == 5
    assert specification["mapped_approved_requirement_keys"] == [
        "gross_floor_area_m2",
        "site_area_m2",
        "storey_count",
    ]
    assert specification["retained_approved_requirement_keys"] == [
        "budget_cap_sgd",
        "step_free_access",
    ]

    scenario = trace["scenario_handoff"]
    assert scenario["field_count"] == 16
    assert scenario["sourced_field_count"] == scenario["field_count"]
    assert scenario["source_coverage"] == 1.0
    assert len(scenario["field_sources"]) == scenario["field_count"]
    assert all(source["source_id"] for source in scenario["field_sources"].values())

    massing = trace["massing_search"]
    assert massing["candidate_count"] == 96
    assert massing["feasible_candidate_count"] > 0
    assert massing["approved_storey_eligible_count"] > 0
    selected_floors = {
        mass["floors"] for mass in massing["selected_candidate"]["candidate"]["masses"]
    }
    assert selected_floors == {scenario["requested_storey_count"]}


def test_missing_required_approval_rejects_handoff() -> None:
    case = workflow_case()
    case["conversation"] = [
        message
        for message in case["conversation"]
        if message["text"] != "I approve the site area of 3,600 m2."
    ]

    with pytest.raises(WorkflowInputError, match="site_area_m2"):
        run_case(case)


def test_invalid_conversation_role_rejects_handoff_with_entry_context() -> None:
    case = workflow_case()
    case["conversation"][0]["role"] = "unverified_role"

    with pytest.raises(WorkflowInputError, match="Invalid conversation entry 1"):
        run_case(case)


def test_unresolved_required_conflict_rejects_handoff() -> None:
    case = workflow_case()
    case["conversation"].append(
        {
            "role": "client",
            "author": "Client Lead",
            "text": "The site area is 4,000 m2.",
        }
    )

    with pytest.raises(WorkflowInputError, match="unresolved conflicts: site_area_m2"):
        run_case(case)


def test_site_area_mismatch_rejects_handoff() -> None:
    case = workflow_case()
    case["site_input"]["site_width_m"] = 61.0

    with pytest.raises(WorkflowInputError, match="Site dimensions imply"):
        run_case(case)


def test_storey_height_conflict_rejects_handoff() -> None:
    case = workflow_case()
    case["site_input"]["max_height_m"] = 15.0

    with pytest.raises(WorkflowInputError, match="above the supplied"):
        run_case(case)


def test_no_feasible_storey_matched_candidate_rejects_handoff() -> None:
    case = workflow_case()
    case["massing_search"] = {"candidate_count": 1, "seed": 0}

    with pytest.raises(WorkflowInputError, match="No feasible candidate"):
        run_case(case)


@pytest.mark.parametrize(
    ("field_path", "value", "message"),
    [
        (("massing_search", "candidate_count"), 0, "candidate_count"),
        (("qs_handoff", "slab_thickness_m"), 0, "slab_thickness_m"),
    ],
)
def test_invalid_numeric_control_rejects_handoff(
    field_path: tuple[str, str], value: int, message: str
) -> None:
    case = workflow_case()
    case[field_path[0]][field_path[1]] = value

    with pytest.raises(WorkflowInputError, match=message):
        run_case(case)


def test_selected_candidate_provenance_survives_qs_handoff() -> None:
    trace = run_case()
    selected_id = trace["massing_search"]["selected_candidate"]["candidate"]["candidate_id"]
    qs = trace["schematic_qs_handoff"]

    assert qs["derivation_source_candidate_id"] == selected_id
    assert qs["plan"]["plan_id"] == f"schematic-{selected_id}"
    assert selected_id in qs["plan"]["source_note"]
    assert qs["takeoff"]["plan_id"] == qs["plan"]["plan_id"]
    assert qs["takeoff_line_count"] == qs["priced_line_count"] == 7
    assert qs["unpriced_line_count"] == 0


def test_scope_boundaries_prevent_invalid_budget_and_tender_claims() -> None:
    trace = run_case()

    assert trace["schematic_qs_handoff"]["budget_comparison_performed"] is False
    assert "broader scope" in trace["schematic_qs_handoff"]["budget_comparison_reason"]
    assert trace["tender_stage"]["status"] == "not_run"
    assert "No tender submission" in trace["tender_stage"]["reason"]


def test_trace_and_generated_artifacts_are_deterministic(tmp_path: Path) -> None:
    first = run_case()
    second = run_case(deepcopy(workflow_case()))
    assert first == second

    write_workflow_artifacts(first, tmp_path)
    first_bytes = {
        path.name: path.read_bytes() for path in sorted(tmp_path.iterdir()) if path.is_file()
    }
    write_workflow_artifacts(second, tmp_path)
    second_bytes = {
        path.name: path.read_bytes() for path in sorted(tmp_path.iterdir()) if path.is_file()
    }
    assert first_bytes == second_bytes

    trace_payload = json.loads((tmp_path / "workflow_trace.json").read_text(encoding="utf-8"))
    candidate_id = first["massing_search"]["selected_candidate"]["candidate"]["candidate_id"]
    assert trace_payload["trace_version"] == first["trace_version"]
    assert candidate_id in (tmp_path / "workflow_trace.svg").read_text(encoding="utf-8")
