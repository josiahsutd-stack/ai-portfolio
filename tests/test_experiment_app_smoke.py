from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("relative_path", "expected_title"),
    [
        (
            "experiments/construction-grid-route-planner/app.py",
            "Construction Grid Route Planner",
        ),
        (
            "experiments/robot-telemetry-rule-monitor/app.py",
            "Robot Telemetry Safety Rule Monitor",
        ),
        (
            "experiments/deterministic-research-workflow/app.py",
            "Deterministic Research Workflow",
        ),
        (
            "experiments/local-model-serving-monitoring/app.py",
            "Local Model Serving and Monitoring Scaffold",
        ),
    ],
)
def test_renamed_experiment_app_loads(relative_path: str, expected_title: str) -> None:
    app = AppTest.from_file(str(ROOT / relative_path)).run(timeout=20)

    assert not app.exception
    assert app.title[0].value == expected_title
