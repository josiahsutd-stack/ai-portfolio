from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

from shared.data import read_json

from .planner import GridMap, RobotTask, plan_robot_task

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "sample_data" / "site_tasks.json"

app = FastAPI(title="Construction Robot Task Planner")


class PlanRequest(BaseModel):
    task_id: str


@app.get("/tasks")
def tasks() -> dict[str, object]:
    payload = read_json(DATA_PATH)
    return {"tasks": payload["tasks"], "site_map": payload["site_map"]}


@app.post("/plan")
def plan(payload: PlanRequest) -> dict[str, object]:
    data = read_json(DATA_PATH)
    site_map = GridMap.from_dict(data["site_map"])
    task_payload = next(item for item in data["tasks"] if item["task_id"] == payload.task_id)
    return plan_robot_task(site_map, RobotTask.from_dict(task_payload))
