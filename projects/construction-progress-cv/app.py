from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

import streamlit as st

from construction_progress_cv import (
    build_progress_summary,
    evaluate_classifier,
    load_metadata,
    predict_stage,
    train_stage_classifier,
)

DATA_PATH = PROJECT_ROOT / "sample_data" / "synthetic_progress_metadata.csv"

st.set_page_config(page_title="Construction Progress CV", page_icon="AI", layout="wide")
st.title("Construction Progress Computer Vision Tracker")
st.caption("Synthetic image metadata demo. Replace metadata with real CV detections in production.")

data = load_metadata(DATA_PATH)
model = train_stage_classifier(data)

left, right = st.columns([1.2, 1])
with left:
    st.subheader("Site progress metadata")
    st.dataframe(data.tail(10), use_container_width=True)
    st.subheader("Automated report")
    st.write(build_progress_summary(data))

with right:
    st.subheader("Evaluation")
    metrics = evaluate_classifier(data)
    st.metric("Holdout accuracy", metrics["accuracy"])
    st.text(metrics["report"])

st.subheader("Classify a new observation")
week = st.slider("Week", 1, 40, 18)
zone = st.selectbox("Zone", sorted(data["zone"].unique()))
values = {
    "week": week,
    "zone": zone,
    "foundation_pct": st.slider("Foundation %", 0.0, 100.0, 100.0),
    "structure_pct": st.slider("Structure %", 0.0, 100.0, 65.0),
    "envelope_pct": st.slider("Envelope %", 0.0, 100.0, 35.0),
    "mep_pct": st.slider("MEP %", 0.0, 100.0, 30.0),
    "interior_pct": st.slider("Interior %", 0.0, 100.0, 10.0),
    "handover_pct": st.slider("Handover %", 0.0, 100.0, 0.0),
    "safety_observations": st.number_input("Safety observations", min_value=0, value=1),
    "weather_delay_days": st.number_input("Weather delay days", min_value=0, value=0),
}
st.success(f"Predicted progress stage: {predict_stage(model, values)}")
