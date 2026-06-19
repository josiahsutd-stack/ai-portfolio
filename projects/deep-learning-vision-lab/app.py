from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

import streamlit as st

from deep_learning_vision_lab import (
    ThresholdVisionModel,
    evaluate_predictions,
    generate_defect_dataset,
)

st.set_page_config(
    page_title="Vision Baseline / Threshold Model Lab", page_icon="AI", layout="wide"
)
st.title("Vision Baseline / Threshold Model Lab")
st.caption(
    "Classical threshold baseline over synthetic images; no neural-network weights are trained."
)
images, labels = generate_defect_dataset()
preds = ThresholdVisionModel().predict(images)
st.json(evaluate_predictions(labels, preds))
st.image(
    images[:6],
    caption=[
        f"label={int(label)} pred={int(pred)}"
        for label, pred in zip(labels[:6], preds[:6], strict=True)
    ],
)
