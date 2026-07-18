from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

import streamlit as st

from agentic_research_ops_assistant import ResearchAgent

st.set_page_config(page_title="Deterministic Research Workflow", page_icon="AI", layout="wide")
st.title("Deterministic Research Workflow Assistant")
st.caption(
    "Planner-executor agent with local RAG, tool calls, citations, trace, and approval checkpoint."
)

task = st.text_area("Research task", "Compare three AI model deployment strategies.")
agent = ResearchAgent(PROJECT_ROOT / "sample_data" / "local_docs")

with st.expander("Available tool registry"):
    st.json([tool.model_dump() for tool in agent.available_tools()])

if st.button("Run agent", type="primary"):
    trace = agent.run(task)
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
st.dataframe(agent.recent_traces(limit=5), use_container_width=True)
