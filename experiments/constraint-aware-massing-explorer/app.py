from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

import streamlit as st

from constraint_aware_massing_explorer import (
    ObjectiveWeights,
    SiteScenario,
    generate_candidates,
    rank_candidates,
    render_candidate_svg,
)

SCENARIO_PATH = PROJECT_ROOT / "sample_data" / "synthetic_site_scenarios.json"
SCENARIO_ROWS = json.loads(SCENARIO_PATH.read_text(encoding="utf-8"))
SCENARIOS = [SiteScenario.from_dict(row) for row in SCENARIO_ROWS]

st.set_page_config(page_title="Constraint-Aware Massing Explorer", page_icon="CM", layout="wide")
st.title("Constraint-Aware Massing Explorer")
st.caption(
    "Synthetic project constraints · deterministic local search · geometric proxy scores · not code certification"
)

with st.sidebar:
    selected_name = st.selectbox("Scenario", [scenario.name for scenario in SCENARIOS])
    base = next(scenario for scenario in SCENARIOS if scenario.name == selected_name)
    candidate_count = st.slider("Candidates", min_value=24, max_value=240, value=96, step=24)
    seed = st.number_input("Random seed", min_value=0, max_value=9999, value=11, step=1)
    st.subheader("Project constraints")
    target_gfa = st.number_input(
        "Target GFA (m2)",
        min_value=100.0,
        max_value=float(base.max_gfa_m2),
        value=float(base.target_gfa_m2),
        step=100.0,
    )
    max_gfa = st.number_input(
        "Maximum GFA (m2)", min_value=float(target_gfa), value=float(base.max_gfa_m2), step=100.0
    )
    max_height = st.number_input(
        "Maximum height (m)",
        min_value=float(base.floor_to_floor_m),
        value=float(base.max_height_m),
        step=float(base.floor_to_floor_m),
    )
    max_coverage = st.slider(
        "Maximum site coverage",
        min_value=0.15,
        max_value=0.85,
        value=float(base.max_site_coverage),
        step=0.01,
    )
    st.subheader("Objective weights")
    weight_gfa = st.slider("GFA fit", 0.0, 1.0, float(base.weights.gfa_fit), 0.05)
    weight_solar = st.slider("Solar proxy", 0.0, 1.0, float(base.weights.solar), 0.05)
    weight_daylight = st.slider("Daylight proxy", 0.0, 1.0, float(base.weights.daylight), 0.05)
    weight_wind = st.slider("Wind proxy", 0.0, 1.0, float(base.weights.wind), 0.05)
    weight_access = st.slider("Access proxy", 0.0, 1.0, float(base.weights.access), 0.05)
    run_search = st.button("Generate options", type="primary", width="stretch")

weights = ObjectiveWeights(
    gfa_fit=weight_gfa,
    solar=weight_solar,
    daylight=weight_daylight,
    wind=weight_wind,
    access=weight_access,
)
try:
    scenario = replace(
        base,
        target_gfa_m2=float(target_gfa),
        max_gfa_m2=float(max_gfa),
        max_height_m=float(max_height),
        max_site_coverage=float(max_coverage),
        weights=weights,
    )
except ValueError as exc:
    st.error(str(exc))
    st.stop()

state_key = (
    scenario.scenario_id,
    candidate_count,
    int(seed),
    target_gfa,
    max_gfa,
    max_height,
    max_coverage,
    tuple(weights.normalized().values()),
)
if run_search or st.session_state.get("massing_key") != state_key:
    candidates = generate_candidates(
        scenario,
        count=candidate_count,
        seed=int(seed),
        mode="constraint_aware",
    )
    st.session_state["massing_assessments"] = rank_candidates(candidates, scenario)
    st.session_state["massing_key"] = state_key

assessments = st.session_state["massing_assessments"]
feasible = [assessment for assessment in assessments if assessment.feasible]
pareto = [assessment for assessment in feasible if assessment.pareto_optimal]

if not feasible:
    st.warning("No candidate passed the supplied hard constraints. Adjust the inputs or seed.")
    st.stop()

best = feasible[0]
metric_columns = st.columns(5)
metric_columns[0].metric("Feasible", f"{len(feasible)}/{len(assessments)}")
metric_columns[1].metric("Pareto options", len(pareto))
metric_columns[2].metric("Top utility", f"{best.utility_score:.3f}")
metric_columns[3].metric("GFA error", f"{best.metrics['gfa_error_fraction'] * 100:.1f}%")
metric_columns[4].metric("Coverage", f"{best.metrics['coverage'] * 100:.1f}%")

option_pool = pareto or feasible
option_id = st.selectbox(
    "Option",
    [assessment.candidate.candidate_id for assessment in option_pool],
    format_func=lambda candidate_id: next(
        f"{item.candidate.typology.replace('_', ' ').title()} · {candidate_id} · utility {item.utility_score:.3f}"
        for item in option_pool
        if item.candidate.candidate_id == candidate_id
    ),
)
selected = next(item for item in option_pool if item.candidate.candidate_id == option_id)

visual_tab, comparison_tab, constraints_tab = st.tabs(
    ["Selected option", "Pareto comparison", "Constraint record"]
)
with visual_tab:
    svg = render_candidate_svg(scenario, selected)
    st.markdown(
        f'<div class="massing-svg">{svg}</div>'
        "<style>.massing-svg svg{width:100%;height:auto;display:block}</style>",
        unsafe_allow_html=True,
    )

with comparison_tab:
    rows = []
    for rank, assessment in enumerate(option_pool[:12], start=1):
        rows.append(
            {
                "rank": rank,
                "id": assessment.candidate.candidate_id,
                "typology": assessment.candidate.typology,
                "utility": assessment.utility_score,
                "GFA m2": assessment.metrics["gfa_m2"],
                "GFA error": assessment.metrics["gfa_error_fraction"],
                "solar proxy": assessment.metrics["solar"],
                "daylight proxy": assessment.metrics["daylight"],
                "wind proxy": assessment.metrics["wind"],
                "access proxy": assessment.metrics["access"],
            }
        )
    st.dataframe(rows, hide_index=True, width="stretch")

with constraints_tab:
    constraint_rows = [
        {"input": "Data status", "value": scenario.data_status, "source": scenario.source_note},
        {
            "input": "Site",
            "value": f"{scenario.site_width_m:.0f} × {scenario.site_depth_m:.0f} m",
            "source": "Bundled scenario",
        },
        {
            "input": "Target / maximum GFA",
            "value": f"{scenario.target_gfa_m2:.0f} / {scenario.max_gfa_m2:.0f} m2",
            "source": "User-editable input",
        },
        {
            "input": "Maximum height",
            "value": f"{scenario.max_height_m:.1f} m",
            "source": "User-editable input",
        },
        {
            "input": "Maximum coverage",
            "value": f"{scenario.max_site_coverage:.2f}",
            "source": "User-editable input",
        },
        {
            "input": "Setbacks N/E/S/W",
            "value": f"{scenario.setback_north_m:.1f} / {scenario.setback_east_m:.1f} / {scenario.setback_south_m:.1f} / {scenario.setback_west_m:.1f} m",
            "source": "Bundled scenario",
        },
    ]
    st.dataframe(constraint_rows, hide_index=True, width="stretch")
    st.info(
        "The access score covers open-site grid routes to a mass edge. It does not model internal travel distance, occupant load, exit width, fire strategy, or statutory egress compliance."
    )
