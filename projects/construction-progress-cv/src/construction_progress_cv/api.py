from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

from .classifier import load_metadata, predict_stage, train_stage_classifier
from .report import build_progress_summary

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "sample_data" / "synthetic_progress_metadata.csv"

app = FastAPI(title="Construction Progress Metadata Classifier")


class ProgressObservation(BaseModel):
    week: int
    zone: str
    foundation_pct: float
    structure_pct: float
    envelope_pct: float
    mep_pct: float
    interior_pct: float
    handover_pct: float
    safety_observations: int = 0
    weather_delay_days: int = 0


@app.get("/summary")
def summary() -> dict[str, str]:
    data = load_metadata(DATA_PATH)
    return {"summary": build_progress_summary(data)}


@app.post("/predict")
def predict(observation: ProgressObservation) -> dict[str, Any]:
    data = load_metadata(DATA_PATH)
    model = train_stage_classifier(data)
    stage = predict_stage(model, observation.model_dump())
    return {"stage": stage, "input": observation.model_dump()}
