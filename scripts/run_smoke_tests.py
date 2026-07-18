from __future__ import annotations

import importlib
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECTS_DIR = ROOT / "projects"
EXPERIMENTS_DIR = ROOT / "experiments"
MODULES = [
    "shared.aec_workflow",
    "aec_code_compliance_rag",
    "qs_takeoff_tender_analysis",
    "bim_schedule_rule_checker",
    "project_specification_copilot",
    "building_energy_regression",
    "constraint_aware_massing_explorer",
    "construction_grid_route_planner",
    "robot_telemetry_rule_monitor",
    "visual_provider_contract",
    "deterministic_research_workflow",
    "vla_embodied_agent_simulator",
    "local_model_serving_monitoring",
    "local_text_classification_lab",
]


def add_project_paths() -> None:
    sys.path.insert(0, str(ROOT))
    for root in (PROJECTS_DIR, EXPERIMENTS_DIR):
        for project in sorted(root.iterdir()):
            src = project / "src"
            if src.exists():
                sys.path.insert(0, str(src))


def check_structure() -> list[str]:
    issues: list[str] = []
    for root in (PROJECTS_DIR, EXPERIMENTS_DIR):
        for project in sorted(root.iterdir()):
            if not project.is_dir() or not any(child.is_file() for child in project.rglob("*")):
                continue
            if not (project / "README.md").exists():
                issues.append(f"{project.name}: missing README.md")
            if not (project / "app.py").exists():
                issues.append(f"{project.name}: missing app.py")
            if not (project / "sample_data").exists():
                issues.append(f"{project.name}: missing sample_data")
    return issues


def check_imports() -> list[str]:
    issues: list[str] = []
    for module in MODULES:
        try:
            importlib.import_module(module)
        except Exception as exc:  # noqa: BLE001 - smoke tests should report all import failures.
            issues.append(f"{module}: import failed: {exc}")
    return issues


def run_core_smoke() -> list[str]:
    issues: list[str] = []
    try:
        from qs_takeoff_tender_analysis import calculate_takeoff, load_floor_plans

        plans = load_floor_plans(
            ROOT
            / "projects"
            / "qs-takeoff-tender-analysis"
            / "sample_data"
            / "synthetic_floor_plans.json"
        )
        if calculate_takeoff(plans[0]).quantity_map()["QTO-FLR"] <= 0:
            issues.append("qs_takeoff_tender_analysis core smoke failed: floor area missing")
    except Exception as exc:  # noqa: BLE001
        issues.append(f"qs_takeoff_tender_analysis core smoke failed: {exc}")
    try:
        from project_specification_copilot import SpecificationEngine

        specification_engine = SpecificationEngine()
        specification_engine.submit_message("client", "The site area is 3,600 m2.")
        if len(specification_engine.snapshot().requirements) != 1:
            issues.append("project_specification_copilot core smoke failed: requirement missing")
    except Exception as exc:  # noqa: BLE001
        issues.append(f"project_specification_copilot core smoke failed: {exc}")
    try:
        from constraint_aware_massing_explorer import SiteScenario, generate_candidates

        scenario = SiteScenario.from_dict(
            {
                "scenario_id": "smoke",
                "name": "Synthetic smoke site",
                "data_status": "synthetic",
                "source_note": "Smoke-test values.",
                "site_width_m": 40,
                "site_depth_m": 30,
                "setbacks_m": {"north": 3, "east": 3, "south": 4, "west": 3},
                "max_height_m": 24,
                "floor_to_floor_m": 3.5,
                "max_site_coverage": 0.5,
                "target_gfa_m2": 2800,
                "max_gfa_m2": 3200,
                "prevailing_wind_from": "south",
                "north_rotation_deg": 0,
                "ingress": {"x": 5, "y": 0},
                "egress": {"x": 35, "y": 0},
            }
        )
        generate_candidates(scenario, count=4, seed=2)
    except Exception as exc:  # noqa: BLE001
        issues.append(f"constraint_aware_massing_explorer core smoke failed: {exc}")
    try:
        from qs_takeoff_tender_analysis import RateLibrary

        from shared.aec_workflow import load_json, run_aec_design_to_cost_workflow

        workflow_case = load_json(
            ROOT
            / "integrations"
            / "aec-design-to-cost"
            / "sample_data"
            / "synthetic_workflow_case.json"
        )
        rates = RateLibrary.from_dict(
            load_json(
                ROOT
                / "projects"
                / "qs-takeoff-tender-analysis"
                / "sample_data"
                / "synthetic_rate_library.json"
            )
        )
        trace = run_aec_design_to_cost_workflow(workflow_case, rates)
        if trace["tender_stage"]["status"] != "not_run":
            issues.append("aec workflow integration core smoke failed: tender boundary missing")
    except Exception as exc:  # noqa: BLE001
        issues.append(f"aec workflow integration core smoke failed: {exc}")
    try:
        from visual_provider_contract import MockVLMProvider

        MockVLMProvider().answer(b"\x89PNG\r\n\x1a\nsmoke", "Extract JSON")
    except Exception as exc:  # noqa: BLE001
        issues.append(f"visual_provider_contract core smoke failed: {exc}")
    try:
        from vla_embodied_agent_simulator import GridWorldEnv

        GridWorldEnv().step("move_right")
    except Exception as exc:  # noqa: BLE001
        issues.append(f"vla_embodied_agent_simulator core smoke failed: {exc}")
    try:
        from local_model_serving_monitoring import generate_churn_data, train_churn_model

        train_churn_model(generate_churn_data(40))
    except Exception as exc:  # noqa: BLE001
        issues.append(f"local_model_serving_monitoring core smoke failed: {exc}")
    try:
        from local_text_classification_lab import train_text_classifier

        with tempfile.TemporaryDirectory() as tmp_dir:
            _model, result = train_text_classifier(output_dir=tmp_dir)
        if result.trained_accuracy <= result.baseline_accuracy:
            issues.append(
                "local_text_classification_lab core smoke failed: trained model did not improve"
            )
    except Exception as exc:  # noqa: BLE001
        issues.append(f"local_text_classification_lab core smoke failed: {exc}")
    return issues


def main() -> None:
    add_project_paths()
    required_docs = [
        ROOT / "docs" / "troubleshooting.md",
        ROOT / "docs" / "how-to-review-this-portfolio.md",
        ROOT / "docs" / "technical-review-guide.md",
        ROOT / "projects" / "projects.yml",
    ]
    issues = [
        f"missing required doc: {path.relative_to(ROOT)}"
        for path in required_docs
        if not path.exists()
    ]
    issues.extend(check_structure())
    issues.extend(check_imports())
    issues.extend(run_core_smoke())
    if issues:
        print("Smoke tests failed:")
        for issue in issues:
            print(f"- {issue}")
        sys.exit(1)
    print(f"Smoke tests passed for {len(MODULES)} importable project modules.")


if __name__ == "__main__":
    main()
