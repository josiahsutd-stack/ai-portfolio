from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI

from .monitor import analyze_telemetry, load_telemetry

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "sample_data" / "synthetic_robot_telemetry.csv"

app = FastAPI(title="Robot Telemetry Safety Rule Monitor")


@app.get("/safety-events")
def safety_events() -> dict[str, object]:
    return analyze_telemetry(load_telemetry(DATA_PATH))
