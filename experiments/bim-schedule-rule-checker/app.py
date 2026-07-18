from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

import streamlit as st

from bim_schedule_rule_checker import (
    detect_issues,
    explain_issue,
    issue_report_markdown,
    load_room_schedule,
)

DATA_PATH = PROJECT_ROOT / "sample_data" / "mock_bim_room_schedule.csv"

st.set_page_config(page_title="BIM Schedule Rule Checker", page_icon="AI", layout="wide")
st.title("BIM Schedule Rule Checker")
st.caption("Synthetic BIM export QA. Findings are demo signals, not professional certification.")

data = load_room_schedule(DATA_PATH)
issues = detect_issues(data)

st.subheader("Mock room schedule")
st.dataframe(data, use_container_width=True)

st.subheader("Detected issues")
st.metric("Issue count", len(issues))
st.dataframe([issue.to_dict() for issue in issues], use_container_width=True)

if issues:
    selected = st.selectbox(
        "Explain issue", issues, format_func=lambda issue: f"{issue.room_id} - {issue.issue_type}"
    )
    st.write(explain_issue(selected))

st.download_button(
    "Download markdown issue report",
    issue_report_markdown(issues),
    file_name="bim_issue_report.md",
    mime="text/markdown",
)
