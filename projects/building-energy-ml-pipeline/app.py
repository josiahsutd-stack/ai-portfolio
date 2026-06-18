from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

import streamlit as st

from building_energy_ml_pipeline.model import (
    evaluate_energy_model,
    load_energy_data,
    predict_energy_use,
    train_energy_model,
)

DATA_PATH = PROJECT_ROOT / "sample_data" / "synthetic_building_energy.csv"

st.set_page_config(page_title="Building Energy ML", page_icon="AI", layout="wide")
st.title("Building Energy Prediction ML Pipeline")
st.caption("Synthetic tabular ML demo for energy-use risk estimation.")

data = load_energy_data(DATA_PATH)
model = train_energy_model(data)
metrics = evaluate_energy_model(data)

left, right = st.columns([1.1, 1])
with left:
    st.subheader("Synthetic training data")
    st.dataframe(data.head(20), use_container_width=True)
with right:
    st.subheader("Evaluation")
    st.metric("MAE", metrics["mae"])
    st.metric("R2", metrics["r2"])

st.subheader("Predict energy use")
features = {
    "building_type": st.selectbox("Building type", sorted(data["building_type"].unique())),
    "floor_area_m2": st.number_input("Floor area (m2)", min_value=100.0, value=8500.0),
    "glazing_ratio": st.slider("Glazing ratio", 0.05, 0.9, 0.42),
    "orientation": st.selectbox("Orientation", ["N", "S", "E", "W"]),
    "climate_zone": st.selectbox("Climate zone", sorted(data["climate_zone"].unique())),
    "occupancy": st.number_input("Occupancy", min_value=1, value=420),
    "insulation_score": st.slider("Insulation score", 0.0, 1.0, 0.62),
    "hvac_type": st.selectbox("HVAC type", sorted(data["hvac_type"].unique())),
    "operating_hours_per_week": st.slider("Operating hours per week", 20, 168, 60),
}
prediction = predict_energy_use(model, features)
st.success(f"Predicted energy intensity: {prediction} kWh/m2/year")
