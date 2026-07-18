from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

import streamlit as st

from deterministic_research_workflow import ResearchWorkflow

st.set_page_config(page_title="Deterministic Research Workflow", page_icon="AI", layout="wide")
st.title("Deterministic Research Workflow")
st.caption(
    "Rule-based local workflow with retrieval, permissioned tools, citations, traces, and an approval checkpoint."
)

task = st.text_area("Research task", "Compare three AI model deployment strategies.")
workflow = ResearchWorkflow(PROJECT_ROOT / "sample_data" / "local_docs")

with st.expander("Available tool registry"):
    st.json([tool.model_dump() for tool in workflow.available_tools()])

if st.button("Run workflow", type="primary"):
    trace = workflow.run(task)
    st.subheader("Plan")
    st.write(trace.plan)
    st.subheader("Tool trace")
    st.json([call.model_dump() for call in trace.tool_calls])
    st.subheader("Citations")
    st.write(trace.citations)
    st.subheader("Trace evaluation")
    st.json(trace.evaluation)
    st.subheader("Final report")
    st.markdown(trace.final_report)

st.subheader("Recent persisted traces")
st.dataframe(workflow.recent_traces(limit=5), width="stretch")
