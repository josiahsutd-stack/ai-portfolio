from __future__ import annotations

import sys
from dataclasses import asdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

import pandas as pd
import streamlit as st

from real_model_finetune_lab import (
    load_examples,
    predict_label,
    train_on_public_dataset,
    train_text_classifier,
)

st.set_page_config(page_title="Local Text Classification Lab", page_icon="AI", layout="wide")
st.title("Local Text Classification Lab")
st.caption("Small scikit-learn text classifier that actually fits model weights locally.")

examples_path = PROJECT_ROOT / "sample_data" / "training_examples.json"
public_dataset_path = PROJECT_ROOT / "sample_data" / "uci_sms_subset.tsv"
model, result = train_text_classifier(examples_path, PROJECT_ROOT / "demo_outputs")
public_model, public_result = train_on_public_dataset(
    public_dataset_path,
    PROJECT_ROOT / "demo_outputs",
)

tab_synthetic, tab_public = st.tabs(["Synthetic quick path", "UCI SMS public subset"])

with tab_synthetic:
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

with tab_public:
    cols = st.columns(4)
    cols[0].metric("Baseline test accuracy", public_result.baseline_test_accuracy)
    cols[1].metric("Trained test accuracy", public_result.test_accuracy)
    cols[2].metric("Validation macro-F1", public_result.validation_macro_f1)
    cols[3].metric("Test macro-F1", public_result.test_macro_f1)

    st.subheader("Public Dataset Result")
    st.json(asdict(public_result))

    st.subheader("Try A Public-Path Prediction")
    sms_text = st.text_area(
        "SMS text",
        "URGENT you have won a free prize claim now",
        height=90,
    )
    st.json(predict_label(public_model, sms_text))

    st.subheader("Public Subset Preview")
    st.dataframe(pd.read_csv(public_dataset_path, sep="\t").head(30), use_container_width=True)
