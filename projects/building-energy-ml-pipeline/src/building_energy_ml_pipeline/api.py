from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

from .model import evaluate_energy_model, load_energy_data, predict_energy_use, train_energy_model

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "sample_data" / "synthetic_building_energy.csv"

app = FastAPI(title="Building Energy Prediction ML Pipeline")


class EnergyPredictionRequest(BaseModel):
    building_type: str
    floor_area_m2: float
    glazing_ratio: float
    orientation: str
    climate_zone: str
    occupancy: int
    insulation_score: float
    hvac_type: str
    operating_hours_per_week: int


@app.get("/metrics")
def metrics() -> dict[str, float]:
    data = load_energy_data(DATA_PATH)
    return evaluate_energy_model(data)


@app.post("/predict")
def predict(payload: EnergyPredictionRequest) -> dict[str, float]:
    data = load_energy_data(DATA_PATH)
    model = train_energy_model(data)
    return {"energy_use_kwh_m2_year": predict_energy_use(model, payload.model_dump())}
