from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

import streamlit as st

from time_series_anomaly_forecasting import (
    detect_anomalies,
    forecast_moving_average,
    generate_series,
    regression_forecast_metrics,
)

st.set_page_config(page_title="Time-Series Anomaly Forecasting", page_icon="AI", layout="wide")
st.title("Time-Series Forecast and Anomaly Baselines")
data = generate_series()
forecast = forecast_moving_average(data)
detected = detect_anomalies(data)
st.json(regression_forecast_metrics(data["value"], forecast))
st.line_chart(data.set_index("t")["value"])
st.dataframe(detected[detected["predicted_anomaly"]], use_container_width=True)
