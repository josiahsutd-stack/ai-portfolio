from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

import streamlit as st

from ai_aec_job_fit_analyzer import analyze_job_description

SAMPLE_JOBS = json.loads(
    (PROJECT_ROOT / "sample_data" / "sample_jobs.json").read_text(encoding="utf-8")
)

st.set_page_config(page_title="AI/AEC Job Description Match", page_icon="AI", layout="wide")
st.title("AI/AEC Job Description Match Baseline")
st.caption("Deterministic keyword matching for AI plus architecture/AEC roles; not a hiring model.")

sample_titles = [job["title"] for job in SAMPLE_JOBS]
selected = st.selectbox("Sample job description", sample_titles)
default_description = next(job["description"] for job in SAMPLE_JOBS if job["title"] == selected)
description = st.text_area("Job description", value=default_description, height=220)

analysis = analyze_job_description(description)

left, right = st.columns([0.8, 1.2])
with left:
    st.metric("Fit score", analysis.fit_score)
    st.metric("Role type", analysis.role_type)
with right:
    st.subheader("Matched skills")
    st.write(", ".join(analysis.matched_skills) or "No direct matches yet.")
    st.subheader("Gaps to address")
    st.write(", ".join(analysis.missing_skills) or "No major extracted gaps.")

st.subheader("Application strategy")
st.write(analysis.application_strategy)
