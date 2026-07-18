from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

import streamlit as st

from llm_evals_guardrails_platform import evaluate_case

st.set_page_config(page_title="LLM Evals Guardrails", page_icon="AI", layout="wide")
st.title("Prompt and Output Validation Checks")
prompt = st.text_area("Prompt", "Return a JSON object with answer and confidence.")
output = st.text_area("Mock output", '{"answer": "Grounded response", "confidence": 0.8}')
st.json(evaluate_case("demo", prompt, output, citations=["doc-1"]).to_dict())
