from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI

from .detector import detect_issues, load_room_schedule

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "sample_data" / "mock_bim_room_schedule.csv"

app = FastAPI(title="BIM Schedule Rule Checker")


@app.get("/issues")
def issues() -> dict[str, object]:
    data = load_room_schedule(DATA_PATH)
    found = detect_issues(data)
    return {"issue_count": len(found), "issues": [issue.to_dict() for issue in found]}
