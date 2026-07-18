from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

import streamlit as st

from fine_tuning_lora_lab import (
    generate_instruction_dataset,
    simulate_lora_run,
    validate_dataset,
)

st.set_page_config(
    page_title="LoRA Dataset and Configuration Validator", page_icon="AI", layout="wide"
)
st.title("LoRA Dataset and Configuration Validator")
rows = generate_instruction_dataset()
st.subheader("Dataset validation")
st.json(validate_dataset(rows))
st.subheader("Simulated run report")
st.json(simulate_lora_run(rows))
