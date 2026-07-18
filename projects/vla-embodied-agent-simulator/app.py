from __future__ import annotations

import json
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
    make_behavior_cloning_policy,
    make_egocentric_policy,
    make_semantic_raster_policy,
    make_synthetic_rgb_policy,
    naive_language_policy,
    random_policy,
    run_episode,
    safety_shielded_policy,
    train_behavior_cloning_policy,
    train_egocentric_policy,
    train_semantic_raster_policy,
    train_synthetic_rgb_policy,
    SYNTHETIC_RGB_SHIFTED_PALETTE,
)

RULE_POLICIES = {
    "Safety shielded": safety_shielded_policy,
    "Naive language": naive_language_policy,
    "Random": random_policy,
}
POLICY_NAMES = [
    "Safety shielded",
    "Engineered-state RF + safety filter",
    "Engineered-state RF raw",
    "Egocentric local-state MLP + safety filter",
    "Egocentric local-state MLP raw",
    "Synthetic RGB MLP + safety filter",
    "Synthetic RGB MLP raw",
    "Synthetic RGB MLP shifted + safety filter",
    "Synthetic RGB MLP shifted raw",
    "Semantic state-raster MLP + safety filter",
    "Semantic state-raster MLP raw",
    "Naive language",
    "Random",
]


@st.cache_resource(show_spinner="Training local imitation policies...")
def learned_policies():
    structured_model, _structured_result = train_behavior_cloning_policy()
    raster_model, _raster_result = train_semantic_raster_policy()
    egocentric_model, _egocentric_result = train_egocentric_policy()
    rgb_model, _rgb_result = train_synthetic_rgb_policy()
    return {
        "Engineered-state RF + safety filter": make_behavior_cloning_policy(
            structured_model,
            safety_filter=True,
        ),
        "Engineered-state RF raw": make_behavior_cloning_policy(
            structured_model,
            safety_filter=False,
        ),
        "Egocentric local-state MLP + safety filter": make_egocentric_policy(
            egocentric_model,
            safety_filter=True,
        ),
        "Egocentric local-state MLP raw": make_egocentric_policy(
            egocentric_model,
            safety_filter=False,
        ),
        "Synthetic RGB MLP + safety filter": make_synthetic_rgb_policy(
            rgb_model,
            safety_filter=True,
        ),
        "Synthetic RGB MLP raw": make_synthetic_rgb_policy(
            rgb_model,
            safety_filter=False,
        ),
        "Synthetic RGB MLP shifted + safety filter": make_synthetic_rgb_policy(
            rgb_model,
            safety_filter=True,
            palette_name=SYNTHETIC_RGB_SHIFTED_PALETTE,
        ),
        "Synthetic RGB MLP shifted raw": make_synthetic_rgb_policy(
            rgb_model,
            safety_filter=False,
            palette_name=SYNTHETIC_RGB_SHIFTED_PALETTE,
        ),
        "Semantic state-raster MLP + safety filter": make_semantic_raster_policy(
            raster_model,
            safety_filter=True,
        ),
        "Semantic state-raster MLP raw": make_semantic_raster_policy(
            raster_model,
            safety_filter=False,
        ),
    }


st.set_page_config(
    page_title="Construction Embodied Agent Simulator",
    page_icon="AI",
    layout="wide",
)
st.title("Construction Embodied Agent Simulator")
st.caption("Local simulation only. No robot hardware, ROS, SLAM, or real actuation.")

scenarios = default_construction_scenarios()
scenario_by_name = {scenario.name: scenario for scenario in scenarios}
selected_scenario = scenario_by_name[
    st.sidebar.selectbox("Scenario", list(scenario_by_name), index=0)
]
policy_name = st.sidebar.selectbox("Policy", POLICY_NAMES, index=3)
instruction = st.text_area("Instruction", selected_scenario.instruction, height=80)

scenario = selected_scenario
if instruction != selected_scenario.instruction:
    scenario = type(selected_scenario)(**{**selected_scenario.__dict__, "instruction": instruction})

policy = RULE_POLICIES.get(policy_name)
if policy is None:
    policy = learned_policies()[policy_name]
episode = run_episode(scenario, policy)
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
    st.dataframe(pd.DataFrame(trace_rows), width="stretch", hide_index=True)

st.subheader("Policy Evaluation")
payload = evaluate_policy_suite(scenarios)
metrics = [{"policy": policy, **values} for policy, values in payload["policies"].items()]
st.dataframe(pd.DataFrame(metrics), width="stretch", hide_index=True)

behavior_path = PROJECT_ROOT / "demo_outputs" / "behavior_cloning_eval_summary.json"
if behavior_path.exists():
    behavior_payload = json.loads(behavior_path.read_text(encoding="utf-8"))
    st.subheader("Learned Policy Holdout Evidence")
    st.caption(
        "Fixed-seed procedural holdout. Train and holdout scenario IDs are disjoint; "
        "failures remain in the published evaluation artifacts. Semantic inputs and rendered "
        "RGB pixels originate from simulator state, not a physical camera. The shifted RGB "
        "condition uses an unseen work-light palette."
    )
    behavior_metrics = [
        {"policy": name, **values} for name, values in behavior_payload["policies"].items()
    ]
    st.dataframe(pd.DataFrame(behavior_metrics), width="stretch", hide_index=True)
    with st.expander("Training and split metadata"):
        st.json(
            {
                "engineered_state_random_forest": behavior_payload["training"],
                "semantic_raster_mlp": behavior_payload["semantic_raster_training"],
                "egocentric_local_state_mlp": behavior_payload["egocentric_training"],
                "synthetic_rgb_mlp": behavior_payload["synthetic_rgb_training"],
                "scenario_id_overlap": behavior_payload["split"]["scenario_id_overlap"],
            }
        )
