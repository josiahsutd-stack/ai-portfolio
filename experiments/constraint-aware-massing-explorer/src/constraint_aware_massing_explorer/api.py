from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .assessment import rank_candidates
from .generation import generate_candidates
from .models import SiteScenario

app = FastAPI(title="Constraint-Aware Massing Explorer")


class SearchRequest(BaseModel):
    scenario: dict[str, object]
    candidate_count: int = Field(default=48, ge=4, le=400)
    seed: int = 7


@app.post("/search")
def search(payload: SearchRequest) -> dict[str, object]:
    scenario = SiteScenario.from_dict(payload.scenario)
    candidates = generate_candidates(
        scenario,
        count=payload.candidate_count,
        seed=payload.seed,
        mode="constraint_aware",
    )
    assessments = rank_candidates(candidates, scenario)
    feasible = [item for item in assessments if item.feasible]
    return {
        "data_status": scenario.data_status,
        "scenario_id": scenario.scenario_id,
        "candidate_count": len(assessments),
        "feasible_count": len(feasible),
        "options": [item.to_dict() for item in feasible[:12]],
        "boundary": "Geometric search with proxy objectives; not code or performance validation.",
    }
