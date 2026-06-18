from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from .monitoring import detect_drift
from .observability import (
    list_drift_reports,
    list_prediction_logs,
    log_prediction,
    record_drift_report,
    save_model_artifact,
)
from .pipeline import generate_churn_data, predict_churn, train_churn_model

app = FastAPI(title="MLOps Model Serving and Monitoring")
REFERENCE_DATA = generate_churn_data()
MODEL, METRICS = train_churn_model(REFERENCE_DATA)
ARTIFACTS = save_model_artifact(MODEL, METRICS)


class ChurnRequest(BaseModel):
    tenure_months: float
    monthly_spend: float
    support_tickets: float
    usage_score: float


@app.get("/metrics")
def metrics() -> dict[str, object]:
    return {"metrics": METRICS, "artifacts": ARTIFACTS}


@app.post("/predict")
def predict(payload: ChurnRequest) -> dict[str, object]:
    request = payload.model_dump()
    prediction = predict_churn(MODEL, request)
    log_id = log_prediction(request, prediction, model_version=str(METRICS["version"]))
    return {**prediction, "model_version": METRICS["version"], "log_id": log_id}


@app.get("/prediction-logs")
def prediction_logs() -> list[dict[str, object]]:
    return list_prediction_logs()


@app.post("/drift-check")
def drift_check(rows: list[ChurnRequest]) -> dict[str, object]:
    import pandas as pd

    current = pd.DataFrame([row.model_dump() for row in rows])
    report = detect_drift(REFERENCE_DATA, current, threshold=0.2)
    report_id = record_drift_report(
        report,
        reference_window="synthetic-reference",
        current_window="api-submitted-batch",
    )
    return {**report, "report_id": report_id}


@app.get("/drift-history")
def drift_history() -> list[dict[str, object]]:
    return list_drift_reports()
