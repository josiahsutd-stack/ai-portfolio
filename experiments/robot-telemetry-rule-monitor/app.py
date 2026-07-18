from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

import streamlit as st

from robot_telemetry_rule_monitor import analyze_telemetry, load_telemetry

DATA_PATH = PROJECT_ROOT / "sample_data" / "synthetic_robot_telemetry.csv"

st.set_page_config(page_title="Robot Telemetry Safety Rule Monitor", page_icon="AI", layout="wide")
st.title("Robot Telemetry Safety Rule Monitor")
st.caption(
    "Synthetic embodied AI safety monitor for construction robots and human-robot work zones."
)

data = load_telemetry(DATA_PATH)
analysis = analyze_telemetry(data)

metrics = st.columns(3)
metrics[0].metric("Safety events", analysis["event_count"])
metrics[1].metric("High severity", analysis["high_count"])
metrics[2].metric("Medium severity", analysis["medium_count"])

st.subheader("Safety summary")
st.write(analysis["summary"])

st.subheader("Synthetic robot telemetry")
st.dataframe(data, width="stretch")

st.subheader("Risk events")
st.dataframe(analysis["events"], width="stretch")
