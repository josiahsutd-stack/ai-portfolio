from __future__ import annotations

import sys
from dataclasses import asdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

import pandas as pd
import streamlit as st

from real_model_finetune_lab import load_examples, predict_label, train_text_classifier

st.set_page_config(page_title="Real Model Fine-Tune Lab", page_icon="AI", layout="wide")
st.title("Real Model Fine-Tune Lab")
st.caption("Small scikit-learn text classifier that actually fits model weights locally.")

examples_path = PROJECT_ROOT / "sample_data" / "training_examples.json"
model, result = train_text_classifier(examples_path, PROJECT_ROOT / "demo_outputs")

cols = st.columns(4)
cols[0].metric("Baseline accuracy", result.baseline_accuracy)
cols[1].metric("Trained accuracy", result.trained_accuracy)
cols[2].metric("Baseline macro-F1", result.baseline_macro_f1)
cols[3].metric("Trained macro-F1", result.trained_macro_f1)

st.subheader("Training Result")
st.json(asdict(result))

st.subheader("Try A Prediction")
text = st.text_area(
    "Text",
    "trace agent tool calls with approval gates and citations",
    height=90,
)
st.json(predict_label(model, text))

st.subheader("Dataset")
rows = [example.__dict__ for example in load_examples(examples_path)]
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
