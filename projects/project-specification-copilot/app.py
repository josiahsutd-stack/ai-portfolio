from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

import streamlit as st

from project_specification_copilot import (
    ROLES,
    SpecificationEngine,
    render_specification_trace_svg,
)

CASES = json.loads(
    (PROJECT_ROOT / "sample_data" / "synthetic_conversations.json").read_text(encoding="utf-8")
)
STRESS_SUMMARY = json.loads(
    (PROJECT_ROOT / "demo_outputs" / "language_stress_summary.json").read_text(encoding="utf-8")
)


def load_case(case_index: int) -> SpecificationEngine:
    engine = SpecificationEngine()
    for row in CASES[case_index]["messages"]:
        engine.submit_message(
            role=row["role"],
            author=row.get("author", row["role"]),
            text=row["text"],
            data_status="synthetic",
        )
    return engine


st.set_page_config(
    page_title="Project Communication and Specification Assistant",
    page_icon="PS",
    layout="wide",
)
st.title("Project Communication and Specification Assistant")
st.caption(
    "Shared role-tagged conversation · synthetic data · deterministic extraction · human-reviewed draft"
)

with st.sidebar:
    case_names = [case["case_id"].replace("-", " ").title() for case in CASES]
    selected_case = st.selectbox("Demo conversation", case_names)
    case_index = case_names.index(selected_case)
    if st.button("Load demo", width="stretch") or st.session_state.get("spec_case") != case_index:
        st.session_state["spec_engine"] = load_case(case_index)
        st.session_state["spec_case"] = case_index
    st.divider()
    active_role = st.selectbox(
        "Active role",
        list(ROLES),
        format_func=lambda role: role.replace("_", " ").title(),
    )
    st.caption("Approval rights depend on requirement category and active role.")

engine: SpecificationEngine = st.session_state["spec_engine"]
snapshot = engine.snapshot()
draft = engine.draft_specification()

metric_columns = st.columns(5)
metric_columns[0].metric("Messages", len(snapshot.messages))
metric_columns[1].metric("Requirements", len(snapshot.requirements))
metric_columns[2].metric(
    "Approved", sum(requirement.status == "approved" for requirement in snapshot.requirements)
)
metric_columns[3].metric(
    "Open conflicts", sum(conflict.status == "open" for conflict in snapshot.conflicts)
)
metric_columns[4].metric("Denied approvals", snapshot.denied_approval_count)

conversation_tab, ledger_tab, specification_tab, language_tab, audit_tab = st.tabs(
    [
        "Conversation",
        "Requirement ledger",
        "Specification draft",
        "Language audit",
        "Audit trace",
    ]
)

with conversation_tab:
    st.caption(
        "Messages remain in the audit record even when the deterministic extractor finds no requirement."
    )
    for message in snapshot.messages:
        with st.chat_message("user" if message.role == "client" else "assistant"):
            st.markdown(
                f"**{message.author} | {message.role.replace('_', ' ').title()} | {message.message_id}**"
            )
            st.write(message.text)
    new_message = st.chat_input("Add a project message")
    if new_message:
        engine.submit_message(active_role, new_message, active_role.replace("_", " ").title())
        st.rerun()

with ledger_tab:
    requirement_rows = [
        {
            "id": requirement.requirement_id,
            "category": requirement.category,
            "requirement": requirement.statement,
            "value": str(requirement.value),
            "unit": requirement.unit or "",
            "status": requirement.status,
            "proposed by": requirement.proposed_by_role,
            "approved by": requirement.approved_by_role or "",
            "sources": ", ".join(requirement.source_message_ids),
        }
        for requirement in snapshot.requirements
    ]
    st.dataframe(requirement_rows, hide_index=True, width="stretch")
    proposed = [
        requirement
        for requirement in snapshot.requirements
        if requirement.status in {"proposed", "approved"}
    ]
    if proposed:
        selected_requirement = st.selectbox(
            "Requirement action",
            [requirement.requirement_id for requirement in proposed],
            format_func=lambda requirement_id: next(
                f"{item.requirement_id} | {item.statement} | {item.status}"
                for item in proposed
                if item.requirement_id == requirement_id
            ),
        )
        if st.button("Record approval", type="primary"):
            engine.submit_message(
                active_role,
                f"I approve {selected_requirement}.",
                active_role.replace("_", " ").title(),
            )
            st.rerun()
    conflict_rows = [
        {
            "id": conflict.conflict_id,
            "key": conflict.requirement_key,
            "requirements": ", ".join(conflict.requirement_ids),
            "status": conflict.status,
            "resolution": conflict.resolution_requirement_id or "",
        }
        for conflict in snapshot.conflicts
    ]
    if conflict_rows:
        st.subheader("Conflict register")
        st.dataframe(conflict_rows, hide_index=True, width="stretch")

with specification_tab:
    svg = render_specification_trace_svg(snapshot, draft)
    st.markdown(
        f'<div class="spec-trace">{svg}</div>'
        "<style>.spec-trace svg{width:100%;height:auto;display:block}</style>",
        unsafe_allow_html=True,
    )
    st.markdown(draft.markdown)

with language_tab:
    stress_metrics = STRESS_SUMMARY["metrics"]
    stress_columns = st.columns(4)
    stress_columns[0].metric("Cases", STRESS_SUMMARY["case_count"])
    stress_columns[1].metric("Extraction F1", f"{stress_metrics['requirement_f1']:.3f}")
    stress_columns[2].metric("Exact cases", f"{stress_metrics['exact_case_accuracy']:.3f}")
    stress_columns[3].metric(
        "Negative controls", f"{stress_metrics['negative_control_accuracy']:.3f}"
    )
    stress_svg = (PROJECT_ROOT / "demo_outputs" / "language_stress_comparison.svg").read_text(
        encoding="utf-8"
    )
    st.markdown(
        f'<div class="language-stress">{stress_svg}</div>'
        "<style>.language-stress svg{width:100%;height:auto;display:block}</style>",
        unsafe_allow_html=True,
    )
    stress_failures = [
        {
            "case": result["case_id"],
            "text": result["text"],
            "missing": json.dumps(result["missing_requirements"]),
            "unexpected": json.dumps(result["unexpected_requirements"]),
        }
        for result in STRESS_SUMMARY["case_results"]
        if not result["exact_match"]
    ]
    st.dataframe(stress_failures, hide_index=True, width="stretch")
    st.caption(
        "Manually labeled synthetic cases; not blinded, independently validated, or representative of open-domain project communication."
    )

with audit_tab:
    audit_rows = [
        {
            "event": event.event_id,
            "type": event.event_type,
            "payload": json.dumps(event.payload, sort_keys=True),
        }
        for event in engine.store.events()
    ]
    st.dataframe(audit_rows, hide_index=True, width="stretch")
    st.info(
        "The bundled parser covers documented requirement forms only. Unrecognized language remains in the message record and does not become a specification clause."
    )
