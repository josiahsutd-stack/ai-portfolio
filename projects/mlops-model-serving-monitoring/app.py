from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

import streamlit as st

from mlops_model_serving_monitoring import (
    detect_drift,
    generate_monitoring_report,
    generate_churn_data,
    list_drift_reports,
    list_prediction_logs,
    log_prediction,
    predict_churn,
    record_drift_report,
    save_model_artifact,
    train_churn_model,
)

st.set_page_config(page_title="MLOps Model Serving", page_icon="AI", layout="wide")
st.title("MLOps Model Serving and Monitoring Platform")
data = generate_churn_data()
model, metrics = train_churn_model(data)
artifacts = save_model_artifact(model, metrics)
current = data.copy()
current["usage_score"] = current["usage_score"] * 0.6
drift_report = detect_drift(data, current)
record_drift_report(
    drift_report,
    reference_window="synthetic-reference",
    current_window="synthetic-current-demo",
)
st.subheader("Model metrics")
st.json(metrics)
st.subheader("Model artifact")
st.json(artifacts)
st.subheader("Drift report")
st.json(drift_report)
st.subheader("Monitoring report")
st.json(generate_monitoring_report(data, current, prediction_logs=list_prediction_logs(limit=20)))

st.subheader("Prediction logging")
with st.form("prediction"):
    tenure = st.number_input("Tenure months", 1.0, 60.0, 12.0)
    spend = st.number_input("Monthly spend", 0.0, 250.0, 80.0)
    tickets = st.number_input("Support tickets", 0.0, 20.0, 3.0)
    usage = st.number_input("Usage score", 0.0, 1.0, 0.6)
    submitted = st.form_submit_button("Predict and log")
if submitted:
    payload = {
        "tenure_months": tenure,
        "monthly_spend": spend,
        "support_tickets": tickets,
        "usage_score": usage,
    }
    prediction = predict_churn(model, payload)
    log_id = log_prediction(
        payload,
        prediction,
        model_version=str(metrics["version"]),
        request_id=f"demo-{len(list_prediction_logs(limit=100)) + 1}",
        latency_ms=12,
    )
    st.success(f"Prediction logged as row {log_id}")
    st.json(prediction)

st.subheader("Recent prediction logs")
st.dataframe(list_prediction_logs(limit=10), use_container_width=True)
st.subheader("Recent drift history")
st.dataframe(list_drift_reports(limit=10), use_container_width=True)
