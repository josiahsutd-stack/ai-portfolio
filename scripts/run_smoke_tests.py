from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECTS_DIR = ROOT / "projects"
MODULES = [
    "aec_code_compliance_rag",
    "construction_progress_cv",
    "bim_issue_detection_agent",
    "ai_aec_job_fit_analyzer",
    "building_energy_ml_pipeline",
    "spatial_design_recommender",
    "construction_robot_task_planner",
    "site_robot_safety_monitor",
    "multimodal_vlm_visual_qa",
    "agentic_research_ops_assistant",
    "vla_embodied_agent_simulator",
    "reinforcement_learning_portfolio",
    "deep_learning_vision_lab",
    "llm_evals_guardrails_platform",
    "mlops_model_serving_monitoring",
    "recommender_system_ranking_engine",
    "time_series_anomaly_forecasting",
    "fine_tuning_lora_lab",
]


def add_project_paths() -> None:
    sys.path.insert(0, str(ROOT))
    for project in sorted(PROJECTS_DIR.iterdir()):
        src = project / "src"
        if src.exists():
            sys.path.insert(0, str(src))


def check_structure() -> list[str]:
    issues: list[str] = []
    for project in sorted(PROJECTS_DIR.iterdir()):
        if not project.is_dir():
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
        from multimodal_vlm_visual_qa import MockVLMProvider

        MockVLMProvider().answer(b"\x89PNG\r\n\x1a\nsmoke", "Extract JSON")
    except Exception as exc:  # noqa: BLE001
        issues.append(f"multimodal_vlm_visual_qa core smoke failed: {exc}")
    try:
        from vla_embodied_agent_simulator import GridWorldEnv

        GridWorldEnv().step("move_right")
    except Exception as exc:  # noqa: BLE001
        issues.append(f"vla_embodied_agent_simulator core smoke failed: {exc}")
    try:
        from reinforcement_learning_portfolio import WarehouseInventoryEnv

        env = WarehouseInventoryEnv()
        env.reset()
        env.step(5)
    except Exception as exc:  # noqa: BLE001
        issues.append(f"reinforcement_learning_portfolio core smoke failed: {exc}")
    try:
        from mlops_model_serving_monitoring import generate_churn_data, train_churn_model

        train_churn_model(generate_churn_data(40))
    except Exception as exc:  # noqa: BLE001
        issues.append(f"mlops_model_serving_monitoring core smoke failed: {exc}")
    return issues


def main() -> None:
    add_project_paths()
    required_docs = [
        ROOT / "docs" / "troubleshooting.md",
        ROOT / "docs" / "how-to-review-this-portfolio.md",
        ROOT / "docs" / "interview-prep.md",
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
