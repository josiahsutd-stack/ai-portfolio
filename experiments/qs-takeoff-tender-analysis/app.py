from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

import streamlit as st

from qs_takeoff_tender_analysis import (
    analyze_tender,
    build_cost_estimate,
    calculate_takeoff,
    load_floor_plans,
    load_rate_library,
    load_tenders,
    render_cost_breakdown_svg,
    render_floor_plan_svg,
    render_tender_comparison_svg,
    review_flags,
)

DATA_DIR = PROJECT_ROOT / "sample_data"
PLANS = load_floor_plans(DATA_DIR / "synthetic_floor_plans.json")
RATES = load_rate_library(DATA_DIR / "synthetic_rate_library.json")
BENCHMARK_PLAN_ID, TENDERS = load_tenders(DATA_DIR / "synthetic_tenders.json")


def show_svg(svg: str, class_name: str) -> None:
    st.markdown(
        f'<div class="{class_name}">{svg}</div>'
        f"<style>.{class_name} svg{{width:100%;height:auto;display:block}}</style>",
        unsafe_allow_html=True,
    )


st.set_page_config(
    page_title="QS Takeoff and Tender Analysis Workbench",
    page_icon="QS",
    layout="wide",
)
st.title("QS Takeoff and Tender Analysis Workbench")
st.caption(
    "Synthetic vector plans | synthetic SGD rates | synthetic anonymous tenders | deterministic local calculations"
)

with st.sidebar:
    selected_name = st.selectbox("Floor-plan fixture", [plan.name for plan in PLANS])
    st.caption(f"Rate set: {RATES.version}")
    st.caption("No PDF, CAD, BIM, OCR, or live market data")

plan = next(plan for plan in PLANS if plan.name == selected_name)
takeoff = calculate_takeoff(plan)
estimate = build_cost_estimate(takeoff, RATES)
quantity_map = takeoff.quantity_map()

metrics = st.columns(5)
metrics[0].metric("Measured floor area", f"{quantity_map['QTO-FLR']:.1f} m2")
metrics[1].metric("External walling", f"{quantity_map['QTO-EXT']:.1f} m2")
metrics[2].metric("Partition walling", f"{quantity_map['QTO-INT']:.1f} m2")
metrics[3].metric("Synthetic base estimate", f"SGD {estimate.base_total:,.0f}")
metrics[4].metric("Illustrative range", f"{estimate.low_total:,.0f}-{estimate.high_total:,.0f}")

plan_tab, cost_tab, tender_tab, audit_tab = st.tabs(
    ["Vector takeoff", "Cost build-up", "Tender exceptions", "Audit record"]
)

with plan_tab:
    show_svg(render_floor_plan_svg(plan, takeoff), "qs-plan-svg")
    st.dataframe(
        [
            {
                "code": line.item_code,
                "description": line.description,
                "quantity": line.quantity,
                "unit": line.unit,
                "formula": line.formula,
                "source geometry": ", ".join(line.source_refs),
            }
            for line in takeoff.quantities
        ],
        hide_index=True,
        width="stretch",
    )

with cost_tab:
    show_svg(render_cost_breakdown_svg(estimate), "qs-cost-svg")
    st.dataframe(
        [
            {
                "code": line.item_code,
                "quantity": line.quantity,
                "unit": line.unit,
                "unit rate": line.unit_rate,
                "base amount": line.amount,
                "low": line.low_amount,
                "high": line.high_amount,
                "rate provenance": line.rate_provenance,
            }
            for line in estimate.priced_lines
        ],
        hide_index=True,
        width="stretch",
    )

with tender_tab:
    benchmark_plan = next(item for item in PLANS if item.plan_id == BENCHMARK_PLAN_ID)
    benchmark = build_cost_estimate(calculate_takeoff(benchmark_plan), RATES)
    analyses = [analyze_tender(tender, benchmark) for tender in TENDERS]
    show_svg(render_tender_comparison_svg(analyses), "qs-tender-svg")
    selected_tender = st.selectbox(
        "Tender fixture", [analysis.bidder_alias for analysis in analyses]
    )
    analysis = next(item for item in analyses if item.bidder_alias == selected_tender)
    flags = review_flags(analysis)
    st.dataframe(
        [
            {
                "item": flag.item_code,
                "exception": flag.flag,
                "benchmark": flag.benchmark_amount,
                "submitted": flag.submitted_amount,
                "ratio": flag.ratio_to_benchmark,
            }
            for flag in flags
        ],
        hide_index=True,
        width="stretch",
    )
    if not flags:
        st.success("No exceptions under the configured synthetic comparison bands.")

with audit_tab:
    st.dataframe(
        [
            {"record": "Plan", "value": plan.plan_id, "provenance": plan.source_note},
            {
                "record": "Scale",
                "value": f"{plan.scale_m_per_unit:g} m per {plan.drawing_unit}",
                "provenance": "Explicit plan field",
            },
            {
                "record": "Rate library",
                "value": RATES.version,
                "provenance": RATES.source_note,
            },
            {
                "record": "Estimate status",
                "value": estimate.status,
                "provenance": "All seven demo quantities matched to versioned rates",
            },
        ],
        hide_index=True,
        width="stretch",
    )
    st.warning(
        "This output is a software demonstration, not a bill of quantities, cost plan, tender recommendation, or professional QS service."
    )
