from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

import pandas as pd
import streamlit as st

from vla_embodied_agent_simulator import (
    GridWorldEnv,
    default_construction_scenarios,
    evaluate_policy_suite,
    naive_language_policy,
    random_policy,
    run_episode,
    safety_shielded_policy,
)

POLICIES = {
    "Safety shielded": safety_shielded_policy,
    "Naive language": naive_language_policy,
    "Random": random_policy,
}

st.set_page_config(page_title="VLA Embodied Agent Simulator", page_icon="AI", layout="wide")
st.title("Construction Site VLA Agent Simulator")
st.caption("Local simulation only. No robot hardware, ROS, SLAM, or real actuation.")

scenarios = default_construction_scenarios()
scenario_by_name = {scenario.name: scenario for scenario in scenarios}
selected_scenario = scenario_by_name[
    st.sidebar.selectbox("Scenario", list(scenario_by_name), index=0)
]
policy_name = st.sidebar.selectbox("Policy", list(POLICIES), index=0)
instruction = st.text_area("Instruction", selected_scenario.instruction, height=80)

scenario = selected_scenario
if instruction != selected_scenario.instruction:
    scenario = type(selected_scenario)(**{**selected_scenario.__dict__, "instruction": instruction})

episode = run_episode(scenario, POLICIES[policy_name])
env = GridWorldEnv.from_scenario(scenario)
for action in [step["action"] for step in episode.trace]:
    env.step(str(action))

summary_cols = st.columns(5)
summary_cols[0].metric("Success", "yes" if episode.success else "no")
summary_cols[1].metric("Steps", episode.steps)
summary_cols[2].metric("Reward", episode.total_reward)
summary_cols[3].metric("Blocked", episode.blocked_action_count)
summary_cols[4].metric("Unsafe rate", round(episode.unsafe_action_count / max(1, episode.steps), 3))

left, right = st.columns([1, 1])
with left:
    st.subheader("Final Grid")
    st.code(env.render_text())
    st.subheader("Scenario State")
    st.json(GridWorldEnv.from_scenario(scenario).state())

with right:
    st.subheader("Episode Trace")
    trace_rows = [
        {
            "step": row["step"],
            "action": row["action"],
            "reward": row["reward"],
            "done": row["done"],
            "info": row["info"],
            "agent": row["state"]["agent"],
            "carrying": row["state"]["carrying"],
        }
        for row in episode.trace
    ]
    st.dataframe(pd.DataFrame(trace_rows), use_container_width=True, hide_index=True)

st.subheader("Policy Evaluation")
payload = evaluate_policy_suite(scenarios)
metrics = [{"policy": policy, **values} for policy, values in payload["policies"].items()]
st.dataframe(pd.DataFrame(metrics), use_container_width=True, hide_index=True)
