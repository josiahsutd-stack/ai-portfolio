from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

import streamlit as st

from aec_code_compliance_rag import build_assistant_from_paths

st.set_page_config(page_title="AEC Code Compliance RAG", page_icon="AI", layout="wide")

st.title("AEC Code Compliance RAG Assistant")
st.caption("Synthetic demo data. Not legal, code, or professional compliance advice.")

docs = sorted((PROJECT_ROOT / "sample_data").glob("*.md"))
assistant = build_assistant_from_paths(docs)

question = st.text_input(
    "Ask a design-standard question",
    value="What should I check for accessible door clearances and routes?",
)
k = st.slider("Retrieved sources", min_value=1, max_value=6, value=4)

if st.button("Answer", type="primary") or question:
    result = assistant.answer(question, k=k)
    st.subheader("Grounded answer")
    st.write(result["answer"])
    st.subheader("Sources")
    for source in result["sources"]:
        with st.expander(f"{source['source']} - score {source['score']}"):
            st.write(source["excerpt"])
