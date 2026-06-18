from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

import streamlit as st

from multimodal_vlm_visual_qa import get_vlm_provider

st.set_page_config(page_title="Multimodal VLM Visual QA", page_icon="AI", layout="wide")
st.title("Multimodal VLM Visual QA Assistant")
st.caption(
    "Mock mode runs without API keys. Set VLM_PROVIDER=openai and OPENAI_API_KEY "
    "to use an OpenAI-compatible vision model."
)

if "history" not in st.session_state:
    st.session_state.history = []

uploaded = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "gif", "webp"])
question = st.text_input("Question", "Extract visible issues as structured JSON.")

if st.button("Analyze", type="primary") and uploaded:
    response = get_vlm_provider().answer(uploaded.getvalue(), question)
    st.session_state.history.append(response.model_dump())
    st.subheader("Answer")
    st.write(response.answer)
    st.subheader("Structured JSON")
    st.json(response.structured_json.model_dump())
    st.metric("Confidence", response.confidence)
    st.info(response.uncertainty)

st.subheader("History")
st.json(st.session_state.history[-5:])
