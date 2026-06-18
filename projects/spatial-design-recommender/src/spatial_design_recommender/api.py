from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from .scoring import DesignScenario, recommend_design_actions, score_design

app = FastAPI(title="Spatial Design Recommendation Engine")


class ScenarioRequest(BaseModel):
    name: str
    floor_area_m2: float
    room_count: int
    avg_daylight_score: float
    circulation_ratio: float
    adjacency_priority: str
    public_private_separation: float


@app.post("/recommend")
def recommend(payload: ScenarioRequest) -> dict[str, object]:
    scenario = DesignScenario.from_dict(payload.model_dump())
    return {
        "score": score_design(scenario),
        "recommendations": [item.to_dict() for item in recommend_design_actions(scenario)],
    }
