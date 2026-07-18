from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

import streamlit as st

from spatial_design_recommender import DesignScenario, recommend_design_actions, score_design

SCENARIOS = json.loads(
    (PROJECT_ROOT / "sample_data" / "example_scenarios.json").read_text(encoding="utf-8")
)

st.set_page_config(page_title="Spatial Design Scoring Baseline", page_icon="AI", layout="wide")
st.title("Spatial Design Scoring Baseline")
st.caption("Explainable recommendation demo for built-environment layout decisions.")

selected = st.selectbox("Example scenario", [scenario["name"] for scenario in SCENARIOS])
base = next(scenario for scenario in SCENARIOS if scenario["name"] == selected)

with st.form("scenario"):
    name = st.text_input("Scenario name", value=base["name"])
    floor_area = st.number_input(
        "Floor area (m2)", min_value=50.0, value=float(base["floor_area_m2"])
    )
    room_count = st.number_input("Room count", min_value=1, value=int(base["room_count"]))
    daylight = st.slider("Average daylight score", 0.0, 1.0, float(base["avg_daylight_score"]))
    circulation = st.slider("Circulation ratio", 0.05, 0.6, float(base["circulation_ratio"]))
    adjacency = st.text_input("Adjacency priority", value=base["adjacency_priority"])
    separation = st.slider(
        "Public/private separation", 0.0, 1.0, float(base["public_private_separation"])
    )
    submitted = st.form_submit_button("Generate recommendations", type="primary")

if submitted or True:
    scenario = DesignScenario(
        name=name,
        floor_area_m2=floor_area,
        room_count=room_count,
        avg_daylight_score=daylight,
        circulation_ratio=circulation,
        adjacency_priority=adjacency,
        public_private_separation=separation,
    )
    st.metric("Design score", score_design(scenario))
    st.subheader("Recommended actions")
    for item in recommend_design_actions(scenario):
        with st.expander(f"{item.priority.title()} priority - {item.category}"):
            st.write(item.rationale)
            st.info(item.action)
