from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from .recommender import content_recommend, generate_interactions, popularity_recommend

app = FastAPI(title="Content-Based Ranking Baseline")


class RecommendationRequest(BaseModel):
    profile: str
    k: int = 3


@app.post("/recommend")
def recommend(payload: RecommendationRequest) -> dict[str, object]:
    items, interactions = generate_interactions()
    return {
        "content_based": content_recommend(items, payload.profile, payload.k),
        "popularity_baseline": popularity_recommend(interactions, payload.k),
    }
