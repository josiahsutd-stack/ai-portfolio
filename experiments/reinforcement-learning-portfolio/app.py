from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

import streamlit as st

from reinforcement_learning_portfolio import (
    DynamicPricingEnv,
    WarehouseInventoryEnv,
    evaluate_policy,
    heuristic_inventory_policy,
    random_policy,
)

st.set_page_config(page_title="RL Portfolio", page_icon="AI", layout="wide")
st.title("Sequential Decision Simulation Baselines")
choice = st.selectbox("Environment", ["Warehouse Inventory Control", "Dynamic Pricing"])
env = WarehouseInventoryEnv() if choice.startswith("Warehouse") else DynamicPricingEnv()
policy = heuristic_inventory_policy if choice.startswith("Warehouse") else random_policy
st.json(evaluate_policy(env, policy, episodes=8))
