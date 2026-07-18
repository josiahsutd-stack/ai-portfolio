from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

import streamlit as st

from recommender_system_ranking_engine import (
    content_recommend,
    generate_interactions,
    popularity_recommend,
)

st.set_page_config(page_title="Recommender Ranking Engine", page_icon="AI", layout="wide")
st.title("Content-Based Ranking Baseline")
items, interactions = generate_interactions()
profile = st.text_input("User interest profile", "LLM agents multimodal robotics")
st.subheader("Content recommendations")
st.json(content_recommend(items, profile))
st.subheader("Popularity baseline")
st.write(popularity_recommend(interactions))
