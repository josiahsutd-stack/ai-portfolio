from __future__ import annotations

from fastapi import FastAPI

from .dataset import generate_defect_dataset
from .model import ThresholdVisionModel, evaluate_predictions

app = FastAPI(title="Vision Baseline / Threshold Model Lab")


@app.get("/metrics")
def metrics() -> dict[str, float]:
    images, labels = generate_defect_dataset()
    preds = ThresholdVisionModel().predict(images)
    return evaluate_predictions(labels, preds)
