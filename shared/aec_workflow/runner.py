from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from constraint_aware_massing_explorer import (
    CandidateAssessment,
    SiteScenario,
    generate_candidates,
    rank_candidates,
)
from project_specification_copilot import ProjectSnapshot, SpecificationEngine
from qs_takeoff_tender_analysis import (
    FloorPlan,
    RateLibrary,
    Room,
    build_cost_estimate,
    calculate_takeoff,
)

from .rendering import render_workflow_trace_svg

REQUIRED_APPROVED_KEYS = {
    "gross_floor_area_m2",
    "site_area_m2",
    "storey_count",
}
MAPPED_APPROVED_KEYS = REQUIRED_APPROVED_KEYS
SITE_SCENARIO_FIELDS = (
    "site_width_m",
    "site_depth_m",
    "setbacks_m",
    "max_height_m",
    "floor_to_floor_m",
    "max_site_coverage",
    "max_gfa_m2",
    "prevailing_wind_from",
    "north_rotation_deg",
    "ingress",
    "egress",
    "grid_resolution_m",
    "objective_weights",
)
BOUNDARIES = (
    "The conversation, site record, rates, and resulting geometry are synthetic fixtures.",
    "Only explicitly approved requirements enter the handoff; unresolved required conflicts stop the run.",
    "Site dimensions and regulatory-style limits are supplied inputs, not inferred from conversation or building codes.",
    "The QS handoff measures one schematic ground-floor envelope and is not a whole-building estimate.",
    "Tender analysis is not run because no tender submission belongs to the derived schematic plan.",
    "Every output requires architect, engineer, authority, and quantity-surveyor review before professional use.",
)


class WorkflowInputError(ValueError):
    """Raised when a cross-project handoff lacks approved or sourced inputs."""


def load_json(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise WorkflowInputError("Workflow input must be a JSON object.")
    return payload


def build_specification_snapshot(case: dict[str, Any]) -> ProjectSnapshot:
    if case.get("data_status") != "synthetic":
        raise WorkflowInputError("The bundled workflow conversation must be labeled synthetic.")
    messages = case.get("conversation")
    if not isinstance(messages, list) or not messages:
        raise WorkflowInputError("Workflow input requires a non-empty conversation list.")
    engine = SpecificationEngine()
    for index, message in enumerate(messages, start=1):
        if not isinstance(message, dict):
            raise WorkflowInputError("Every conversation entry must be an object.")
        try:
            engine.submit_message(
                role=str(message.get("role", "")),
                author=str(message.get("author", "")) or None,
                text=str(message.get("text", "")),
                data_status="synthetic",
            )
        except (TypeError, ValueError) as exc:
            raise WorkflowInputError(f"Invalid conversation entry {index}: {exc}") from exc
    return engine.snapshot()


def _approved_by_key(snapshot: ProjectSnapshot) -> dict[str, Any]:
    open_required_conflicts = sorted(
        conflict.requirement_key
        for conflict in snapshot.conflicts
        if conflict.status == "open" and conflict.requirement_key in REQUIRED_APPROVED_KEYS
    )
    if open_required_conflicts:
        raise WorkflowInputError(
            "Required workflow requirements have unresolved conflicts: "
            + ", ".join(open_required_conflicts)
        )
    approved = {
        requirement.key: requirement
        for requirement in snapshot.requirements
        if requirement.status == "approved"
    }
    missing = sorted(REQUIRED_APPROVED_KEYS - approved.keys())
    if missing:
        raise WorkflowInputError(
            "Required workflow requirements are not approved: " + ", ".join(missing)
        )
    return approved


def _build_scenario(
    workflow_case: dict[str, Any], snapshot: ProjectSnapshot
) -> tuple[SiteScenario, dict[str, dict[str, Any]], int]:
    approved = _approved_by_key(snapshot)
    site_input = workflow_case.get("site_input")
    if not isinstance(site_input, dict):
        raise WorkflowInputError("Workflow input requires a site_input object.")
    if site_input.get("data_status") != "synthetic":
        raise WorkflowInputError("The bundled site input must be labeled synthetic.")
    missing_site_fields = sorted(set(SITE_SCENARIO_FIELDS) - site_input.keys())
    if missing_site_fields:
        raise WorkflowInputError("Site input is missing fields: " + ", ".join(missing_site_fields))

    site_area = float(site_input["site_width_m"]) * float(site_input["site_depth_m"])
    approved_site_area = float(approved["site_area_m2"].value)
    if abs(site_area - approved_site_area) > max(0.01, approved_site_area * 0.001):
        raise WorkflowInputError(
            f"Site dimensions imply {site_area:.2f} m2 but approved site area is {approved_site_area:.2f} m2."
        )

    requested_storeys = int(approved["storey_count"].value)
    floor_to_floor = float(site_input["floor_to_floor_m"])
    required_height = requested_storeys * floor_to_floor
    if required_height > float(site_input["max_height_m"]) + 1e-9:
        raise WorkflowInputError(
            f"Approved {requested_storeys}-storey requirement needs {required_height:.2f} m, "
            f"above the supplied {float(site_input['max_height_m']):.2f} m limit."
        )

    site_input_id = str(site_input.get("site_input_id", "unidentified-site-input"))
    scenario_payload = {
        "scenario_id": str(workflow_case.get("workflow_case_id", "aec-workflow")),
        "name": str(workflow_case.get("name", "AEC workflow integration")),
        "data_status": "synthetic",
        "source_note": str(site_input.get("source_note", "Synthetic integration site input.")),
        **{field: site_input[field] for field in SITE_SCENARIO_FIELDS},
        "target_gfa_m2": float(approved["gross_floor_area_m2"].value),
    }
    try:
        scenario = SiteScenario.from_dict(scenario_payload)
    except (KeyError, TypeError, ValueError) as exc:
        raise WorkflowInputError(f"Invalid site scenario: {exc}") from exc

    field_sources = {
        field: {
            "source_type": "synthetic_site_input",
            "source_id": site_input_id,
        }
        for field in SITE_SCENARIO_FIELDS
    }
    field_sources["target_gfa_m2"] = {
        "source_type": "approved_requirement",
        "source_id": approved["gross_floor_area_m2"].requirement_id,
        "source_message_ids": approved["gross_floor_area_m2"].source_message_ids,
    }
    field_sources["requested_storey_count"] = {
        "source_type": "approved_requirement",
        "source_id": approved["storey_count"].requirement_id,
        "source_message_ids": approved["storey_count"].source_message_ids,
    }
    field_sources["site_area_validation_m2"] = {
        "source_type": "approved_requirement_and_site_dimensions",
        "source_id": approved["site_area_m2"].requirement_id,
        "source_message_ids": approved["site_area_m2"].source_message_ids,
    }
    return scenario, field_sources, requested_storeys


def candidate_to_schematic_plan(
    assessment: CandidateAssessment,
    *,
    storey_height_m: float,
    slab_thickness_m: float,
) -> FloorPlan:
    candidate = assessment.candidate
    rooms = tuple(
        Room(
            room_id=f"MASS-{index:02d}",
            name=f"{mass.label} ground-floor envelope",
            x=round(mass.footprint.x, 6),
            y=round(mass.footprint.y, 6),
            width=round(mass.footprint.width, 6),
            depth=round(mass.footprint.depth, 6),
        )
        for index, mass in enumerate(candidate.masses, start=1)
    )
    return FloorPlan(
        plan_id=f"schematic-{candidate.candidate_id}",
        name=f"Schematic ground-floor envelope from {candidate.candidate_id}",
        data_status="synthetic",
        source_note=(
            f"Derived directly from selected massing candidate {candidate.candidate_id}; "
            "mass footprints are treated as room-like rectangles only to exercise the takeoff contract."
        ),
        drawing_unit="m",
        scale_m_per_unit=1.0,
        storey_height_m=storey_height_m,
        slab_thickness_m=slab_thickness_m,
        rooms=rooms,
        openings=(),
    )


def _select_candidate(
    scenario: SiteScenario,
    requested_storeys: int,
    candidate_count: int,
    seed: int,
) -> tuple[CandidateAssessment, list[CandidateAssessment], list[CandidateAssessment]]:
    candidates = generate_candidates(scenario, count=candidate_count, seed=seed)
    ranked = rank_candidates(candidates, scenario)
    feasible = [assessment for assessment in ranked if assessment.feasible]
    eligible = [
        assessment
        for assessment in feasible
        if max(mass.floors for mass in assessment.candidate.masses) == requested_storeys
    ]
    if not eligible:
        raise WorkflowInputError(
            f"No feasible candidate satisfies the approved {requested_storeys}-storey requirement."
        )
    return eligible[0], feasible, eligible


def run_aec_design_to_cost_workflow(
    workflow_case: dict[str, Any], rate_library: RateLibrary
) -> dict[str, Any]:
    if workflow_case.get("data_status") != "synthetic":
        raise WorkflowInputError("The bundled workflow case must be labeled synthetic.")
    if rate_library.data_status != "synthetic":
        raise WorkflowInputError("The bundled rate library must be labeled synthetic.")

    snapshot = build_specification_snapshot(workflow_case)
    approved = _approved_by_key(snapshot)
    scenario, field_sources, requested_storeys = _build_scenario(workflow_case, snapshot)
    search = workflow_case.get("massing_search", {})
    if not isinstance(search, dict):
        raise WorkflowInputError("massing_search must be an object.")
    candidate_count = int(search.get("candidate_count", 96))
    seed = int(search.get("seed", 11))
    if not 1 <= candidate_count <= 5000:
        raise WorkflowInputError("candidate_count must be between 1 and 5000.")
    selected, feasible, eligible = _select_candidate(
        scenario, requested_storeys, candidate_count, seed
    )

    qs_input = workflow_case.get("qs_handoff", {})
    if not isinstance(qs_input, dict):
        raise WorkflowInputError("qs_handoff must be an object.")
    slab_thickness_m = float(qs_input.get("slab_thickness_m", 0.15))
    if slab_thickness_m <= 0:
        raise WorkflowInputError("slab_thickness_m must be positive.")
    plan = candidate_to_schematic_plan(
        selected,
        storey_height_m=scenario.floor_to_floor_m,
        slab_thickness_m=slab_thickness_m,
    )
    takeoff = calculate_takeoff(plan)
    estimate = build_cost_estimate(takeoff, rate_library)

    approved_requirements = sorted(
        (
            {
                "requirement_id": requirement.requirement_id,
                "key": requirement.key,
                "value": requirement.value,
                "unit": requirement.unit,
                "source_message_ids": requirement.source_message_ids,
                "approved_by_role": requirement.approved_by_role,
                "approval_message_id": requirement.approval_message_id,
            }
            for requirement in approved.values()
        ),
        key=lambda item: item["key"],
    )
    retained = sorted(set(approved) - MAPPED_APPROVED_KEYS)
    sourced_field_count = sum(
        1 for source in field_sources.values() if str(source.get("source_id", "")).strip()
    )
    review_gates = (
        "Validate site dimensions, setbacks, access points, height, GFA, and coverage against current survey and authority requirements.",
        "Architect and engineering team review the selected massing geometry and every unmodeled design constraint.",
        "Quantity surveyor defines measurement rules, complete scope, current rates, procurement allowances, and risk.",
        "Client team reviews approved requirements retained outside automation, including budget and accessibility intent.",
    )
    trace: dict[str, Any] = {
        "artifact_schema_version": 1,
        "workflow_case_id": str(workflow_case.get("workflow_case_id", "aec-workflow")),
        "data_status": "synthetic",
        "status": "completed_with_human_review_gates",
        "specification_handoff": {
            "message_count": len(snapshot.messages),
            "approved_requirement_count": len(approved_requirements),
            "mapped_approved_requirement_keys": sorted(MAPPED_APPROVED_KEYS),
            "mapped_approved_requirement_count": len(MAPPED_APPROVED_KEYS),
            "retained_approved_requirement_keys": retained,
            "retained_approved_requirement_count": len(retained),
            "approved_requirements": approved_requirements,
            "open_required_conflict_count": 0,
        },
        "scenario_handoff": {
            "field_count": len(field_sources),
            "sourced_field_count": sourced_field_count,
            "source_coverage": sourced_field_count / len(field_sources),
            "field_sources": field_sources,
            "scenario": scenario.to_dict(),
            "requested_storey_count": requested_storeys,
        },
        "massing_search": {
            "candidate_count": candidate_count,
            "seed": seed,
            "feasible_candidate_count": len(feasible),
            "approved_storey_eligible_count": len(eligible),
            "selection_rule": (
                "Highest-ranked feasible Pareto candidate whose maximum mass height matches the approved storey count."
            ),
            "selected_candidate": selected.to_dict(),
        },
        "schematic_qs_handoff": {
            "scope": "One schematic ground-floor envelope only",
            "derivation_source_candidate_id": selected.candidate.candidate_id,
            "plan": plan.to_dict(),
            "takeoff": takeoff.to_dict(),
            "estimate": estimate.to_dict(),
            "takeoff_line_count": len(takeoff.quantities),
            "priced_line_count": len(estimate.priced_lines),
            "unpriced_line_count": len(estimate.unpriced_item_codes),
            "budget_comparison_performed": False,
            "budget_comparison_reason": (
                "The approved project budget covers a different and much broader scope than this ground-floor proxy."
            ),
        },
        "tender_stage": {
            "status": "not_run",
            "reason": "No tender submission is authored for the derived schematic plan.",
        },
        "human_review_gates": list(review_gates),
        "boundaries": list(BOUNDARIES),
    }
    version_payload = json.dumps(trace, sort_keys=True, separators=(",", ":"))
    trace["trace_version"] = hashlib.sha256(version_payload.encode("utf-8")).hexdigest()[:12]
    return trace


def _render_summary(trace: dict[str, Any]) -> str:
    specification = trace["specification_handoff"]
    scenario = trace["scenario_handoff"]
    massing = trace["massing_search"]
    qs = trace["schematic_qs_handoff"]
    selected = massing["selected_candidate"]
    estimate = qs["estimate"]
    lines = [
        "# AEC Design-To-Cost Integration Trace",
        "",
        "**Data status:** Synthetic integration fixture",
        "**Output status:** Human review required",
        f"**Trace version:** `{trace['trace_version']}`",
        "",
        "## Executed Handoffs",
        "",
        "| Stage | Result |",
        "| --- | --- |",
        f"| Specification ledger | {specification['approved_requirement_count']} approved requirements; {specification['mapped_approved_requirement_count']} mapped; {specification['retained_approved_requirement_count']} retained for review |",
        f"| Scenario contract | {scenario['field_count']} sourced fields; source coverage `{scenario['source_coverage']:.3f}` |",
        f"| Massing search | {massing['candidate_count']} generated; {massing['feasible_candidate_count']} feasible; {massing['approved_storey_eligible_count']} satisfy approved storey count |",
        f"| Selected option | `{selected['candidate']['candidate_id']}`; utility `{selected['utility_score']:.3f}`; GFA `{selected['metrics']['gfa_m2']:.1f} m2` |",
        f"| Schematic takeoff | {qs['takeoff_line_count']} quantity lines; {qs['priced_line_count']} priced; {qs['unpriced_line_count']} unpriced |",
        f"| Illustrative rate build-up | `{estimate['currency']} {estimate['base_total']:,.2f}` for the bounded ground-floor proxy only |",
        "| Tender stage | Not run; no tender belongs to the derived plan |",
        "",
        "## Interpretation",
        "",
        "This fixture demonstrates that the three local project contracts exchange typed, source-linked data and reject incomplete inputs. It does not validate design quality, compliance, commercial completeness, or professional suitability.",
        "",
        "## Human Review Gates",
        "",
        *[f"- {gate}" for gate in trace["human_review_gates"]],
        "",
        "## Boundaries",
        "",
        *[f"- {boundary}" for boundary in trace["boundaries"]],
        "",
    ]
    return "\n".join(lines)


def write_workflow_artifacts(
    trace: dict[str, Any], output_dir: str | Path, site_asset_path: str | Path | None = None
) -> None:
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    (target / "workflow_trace.json").write_text(
        json.dumps(trace, indent=2) + "\n", encoding="utf-8"
    )
    (target / "workflow_summary.md").write_text(_render_summary(trace), encoding="utf-8")
    svg = render_workflow_trace_svg(trace)
    (target / "workflow_trace.svg").write_text(svg, encoding="utf-8")
    if site_asset_path is not None:
        asset = Path(site_asset_path)
        asset.parent.mkdir(parents=True, exist_ok=True)
        asset.write_text(svg, encoding="utf-8")
