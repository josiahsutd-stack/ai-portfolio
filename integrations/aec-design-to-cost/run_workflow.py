from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for source_root in (
    ROOT,
    ROOT / "projects" / "project-specification-copilot" / "src",
    ROOT / "projects" / "constraint-aware-massing-explorer" / "src",
    ROOT / "projects" / "qs-takeoff-tender-analysis" / "src",
):
    sys.path.insert(0, str(source_root))

from qs_takeoff_tender_analysis import RateLibrary  # noqa: E402

from shared.aec_workflow import (  # noqa: E402
    load_json,
    run_aec_design_to_cost_workflow,
    write_workflow_artifacts,
)

INTEGRATION_DIR = Path(__file__).resolve().parent


def main() -> None:
    workflow_case = load_json(INTEGRATION_DIR / "sample_data" / "synthetic_workflow_case.json")
    rate_payload = load_json(
        ROOT
        / "projects"
        / "qs-takeoff-tender-analysis"
        / "sample_data"
        / "synthetic_rate_library.json"
    )
    trace = run_aec_design_to_cost_workflow(
        workflow_case,
        RateLibrary.from_dict(rate_payload),
    )
    write_workflow_artifacts(
        trace,
        INTEGRATION_DIR / "demo_outputs",
        ROOT / "portfolio-site" / "assets" / "aec-workflow-trace.svg",
    )
    print(
        json.dumps(
            {
                "data_status": trace["data_status"],
                "trace_version": trace["trace_version"],
                "approved_requirements": trace["specification_handoff"][
                    "approved_requirement_count"
                ],
                "mapped_requirements": trace["specification_handoff"][
                    "mapped_approved_requirement_count"
                ],
                "retained_requirements": trace["specification_handoff"][
                    "retained_approved_requirement_count"
                ],
                "scenario_source_coverage": trace["scenario_handoff"]["source_coverage"],
                "generated_candidates": trace["massing_search"]["candidate_count"],
                "feasible_candidates": trace["massing_search"]["feasible_candidate_count"],
                "storey_matched_candidates": trace["massing_search"][
                    "approved_storey_eligible_count"
                ],
                "selected_candidate": trace["massing_search"]["selected_candidate"]["candidate"][
                    "candidate_id"
                ],
                "takeoff_lines": trace["schematic_qs_handoff"]["takeoff_line_count"],
                "unpriced_lines": trace["schematic_qs_handoff"]["unpriced_line_count"],
                "tender_stage": trace["tender_stage"]["status"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
