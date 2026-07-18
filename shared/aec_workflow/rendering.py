from __future__ import annotations

from html import escape
from typing import Any


def render_workflow_trace_svg(trace: dict[str, Any]) -> str:
    specification = trace["specification_handoff"]
    scenario_handoff = trace["scenario_handoff"]
    scenario = scenario_handoff["scenario"]
    massing = trace["massing_search"]
    qs = trace["schematic_qs_handoff"]
    selected = massing["selected_candidate"]

    candidate_id = escape(str(selected["candidate"]["candidate_id"]))
    scenario_name = escape(str(scenario["name"]))
    trace_version = escape(str(trace["trace_version"]))
    message_count = specification["message_count"]
    approved_count = specification["approved_requirement_count"]
    mapped_count = specification["mapped_approved_requirement_count"]
    retained_count = specification["retained_approved_requirement_count"]
    conflict_count = specification["open_required_conflict_count"]
    field_count = scenario_handoff["field_count"]
    sourced_field_count = scenario_handoff["sourced_field_count"]
    candidate_count = massing["candidate_count"]
    feasible_count = massing["feasible_candidate_count"]
    eligible_count = massing["approved_storey_eligible_count"]
    gfa_m2 = selected["metrics"]["gfa_m2"]
    utility = selected["utility_score"]
    takeoff_count = qs["takeoff_line_count"]
    priced_count = qs["priced_line_count"]
    review_gate_count = len(trace["human_review_gates"])
    tender_status = escape(str(trace["tender_stage"]["status"]).replace("_", " "))

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="860" viewBox="0 0 1400 860" role="img" aria-labelledby="title desc">
  <title id="title">Executed AEC design-to-cost system journey</title>
  <desc id="desc">Two synthetic input streams pass through source and approval gates into three implemented project modules, with typed handoffs, traceable identifiers, and explicit professional review boundaries.</desc>
  <defs>
    <filter id="shadow" x="-10%" y="-10%" width="120%" height="130%">
      <feDropShadow dx="0" dy="5" stdDeviation="8" flood-color="#17352d" flood-opacity="0.10"/>
    </filter>
    <marker id="arrow-green" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#0e8a6b"/>
    </marker>
    <marker id="arrow-blue" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#345b70"/>
    </marker>
  </defs>

  <rect width="1400" height="860" fill="#f4f7f6"/>
  <rect x="24" y="24" width="1352" height="812" rx="18" fill="#ffffff" stroke="#d9e4df"/>
  <rect x="24" y="24" width="12" height="812" rx="6" fill="#0e8a6b"/>

  <text x="70" y="74" font-family="Arial, sans-serif" font-size="13" font-weight="700" letter-spacing="1.4" fill="#0e8a6b">EXECUTED AEC WORKFLOW / SYNTHETIC FIXTURE</text>
  <text x="70" y="112" font-family="Arial, sans-serif" font-size="30" font-weight="700" fill="#16201d">From approved project intent to a bounded cost input</text>
  <text x="70" y="140" font-family="Arial, sans-serif" font-size="14" fill="#5d6c66">The diagram is generated from the checked-in trace. Each arrow is an implemented, tested handoff rather than a proposed integration.</text>

  <rect x="1112" y="58" width="108" height="30" rx="15" fill="#e8f4ef" stroke="#b9ddcf"/>
  <text x="1166" y="78" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" font-weight="700" fill="#0e8a6b">SYNTHETIC</text>
  <rect x="1230" y="58" width="110" height="30" rx="15" fill="#eef3f6" stroke="#c9d7df"/>
  <text x="1285" y="78" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" font-weight="700" fill="#345b70">TRACE {trace_version}</text>

  <text x="70" y="184" font-family="Arial, sans-serif" font-size="11" font-weight="700" letter-spacing="1.2" fill="#87938e">INPUTS</text>

  <g filter="url(#shadow)">
    <rect x="70" y="200" width="340" height="112" rx="12" fill="#ffffff" stroke="#cddbd5"/>
    <rect x="70" y="200" width="7" height="112" rx="3" fill="#0e8a6b"/>
    <text x="94" y="229" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="#0e8a6b">ROLE-TAGGED CONVERSATION</text>
    <text x="94" y="258" font-family="Arial, sans-serif" font-size="20" font-weight="700" fill="#16201d">{message_count} messages to {approved_count} approvals</text>
    <text x="94" y="284" font-family="Arial, sans-serif" font-size="13" fill="#5d6c66">Client + architect roles / {conflict_count} required conflicts open</text>
    <text x="94" y="302" font-family="Arial, sans-serif" font-size="11" fill="#87938e">MSG identifiers retained as evidence</text>
  </g>

  <g filter="url(#shadow)">
    <rect x="990" y="200" width="340" height="112" rx="12" fill="#ffffff" stroke="#cddbd5"/>
    <rect x="1323" y="200" width="7" height="112" rx="3" fill="#345b70"/>
    <text x="1014" y="229" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="#345b70">SUPPLIED SITE RECORD</text>
    <text x="1014" y="258" font-family="Arial, sans-serif" font-size="20" font-weight="700" fill="#16201d">{scenario_name}</text>
    <text x="1014" y="284" font-family="Arial, sans-serif" font-size="13" fill="#5d6c66">{sourced_field_count}/{field_count} fields source-linked / SITE-FIXTURE-001</text>
    <text x="1014" y="302" font-family="Arial, sans-serif" font-size="11" fill="#87938e">Geometry and limits supplied, not inferred</text>
  </g>

  <path d="M410 256 H500" fill="none" stroke="#0e8a6b" stroke-width="2" marker-end="url(#arrow-green)"/>
  <path d="M990 256 H900" fill="none" stroke="#345b70" stroke-width="2" marker-end="url(#arrow-blue)"/>

  <g filter="url(#shadow)">
    <rect x="500" y="186" width="400" height="140" rx="14" fill="#16201d"/>
    <text x="530" y="218" font-family="Arial, sans-serif" font-size="12" font-weight="700" letter-spacing="1" fill="#d7a441">SOURCE + APPROVAL GATE</text>
    <text x="530" y="250" font-family="Arial, sans-serif" font-size="20" font-weight="700" fill="#ffffff">Only approved + sourced values pass</text>
    <text x="530" y="276" font-family="Arial, sans-serif" font-size="13" fill="#dce7e2">{mapped_count} requirements mapped / {retained_count} held for human review</text>
    <text x="530" y="298" font-family="Arial, sans-serif" font-size="13" fill="#dce7e2">Missing, conflicted, or scope-incompatible inputs fail closed</text>
  </g>

  <path d="M700 326 V354" fill="none" stroke="#0e8a6b" stroke-width="3" marker-end="url(#arrow-green)"/>
  <text x="718" y="345" font-family="Arial, sans-serif" font-size="11" font-weight="700" fill="#0e8a6b">VALIDATED CONTRACT</text>

  <text x="70" y="372" font-family="Arial, sans-serif" font-size="11" font-weight="700" letter-spacing="1.2" fill="#87938e">IMPLEMENTED SYSTEMS AND TYPED HANDOFFS</text>

  <g filter="url(#shadow)">
    <rect x="70" y="390" width="360" height="218" rx="14" fill="#ffffff" stroke="#cddbd5"/>
    <rect x="70" y="390" width="360" height="48" rx="14" fill="#e8f4ef"/>
    <rect x="70" y="424" width="360" height="14" fill="#e8f4ef"/>
    <text x="92" y="420" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="#0e8a6b">01 / COMMUNICATION + SPECIFICATION</text>
    <text x="92" y="472" font-family="Arial, sans-serif" font-size="18" font-weight="700" fill="#16201d">Requirement state machine</text>
    <text x="92" y="500" font-family="Arial, sans-serif" font-size="13" fill="#5d6c66">Versioned values and source-message IDs</text>
    <text x="92" y="523" font-family="Arial, sans-serif" font-size="13" fill="#5d6c66">Role-authorized approvals and conflict gates</text>
    <rect x="92" y="548" width="314" height="38" rx="6" fill="#f4f7f6" stroke="#d9e4df"/>
    <text x="108" y="572" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="#345b70">OUTPUT / REQ IDs + approval evidence</text>
  </g>

  <path d="M430 499 H503" fill="none" stroke="#345b70" stroke-width="2" marker-end="url(#arrow-blue)"/>
  <text x="466" y="487" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" font-weight="700" fill="#345b70">SCENARIO</text>

  <g filter="url(#shadow)">
    <rect x="520" y="390" width="360" height="218" rx="14" fill="#ffffff" stroke="#cddbd5"/>
    <rect x="520" y="390" width="360" height="48" rx="14" fill="#eef3f6"/>
    <rect x="520" y="424" width="360" height="14" fill="#eef3f6"/>
    <text x="542" y="420" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="#345b70">02 / CONSTRAINT-AWARE MASSING</text>
    <text x="542" y="472" font-family="Arial, sans-serif" font-size="18" font-weight="700" fill="#16201d">Bounded option search</text>
    <text x="542" y="500" font-family="Arial, sans-serif" font-size="13" fill="#5d6c66">{candidate_count} candidates / {feasible_count} feasible</text>
    <text x="542" y="523" font-family="Arial, sans-serif" font-size="13" fill="#5d6c66">{eligible_count} match the approved storey count</text>
    <rect x="542" y="548" width="314" height="38" rx="6" fill="#f4f7f6" stroke="#d9e4df"/>
    <text x="558" y="572" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="#345b70">OUTPUT / {candidate_id} / {gfa_m2:.0f} m2 / {utility:.3f}</text>
  </g>

  <path d="M880 499 H953" fill="none" stroke="#345b70" stroke-width="2" marker-end="url(#arrow-blue)"/>
  <text x="916" y="487" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" font-weight="700" fill="#345b70">ENVELOPE</text>

  <g filter="url(#shadow)">
    <rect x="970" y="390" width="360" height="218" rx="14" fill="#ffffff" stroke="#cddbd5"/>
    <rect x="970" y="390" width="360" height="48" rx="14" fill="#f8f1df"/>
    <rect x="970" y="424" width="360" height="14" fill="#f8f1df"/>
    <text x="992" y="420" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="#8a6516">03 / QS TAKEOFF + RATE BUILD-UP</text>
    <text x="992" y="472" font-family="Arial, sans-serif" font-size="18" font-weight="700" fill="#16201d">Schematic quantity contract</text>
    <text x="992" y="500" font-family="Arial, sans-serif" font-size="13" fill="#5d6c66">One ground-floor envelope only</text>
    <text x="992" y="523" font-family="Arial, sans-serif" font-size="13" fill="#5d6c66">{takeoff_count} measured / {priced_count} synthetic-rate lines</text>
    <rect x="992" y="548" width="314" height="38" rx="6" fill="#f4f7f6" stroke="#d9e4df"/>
    <text x="1008" y="572" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="#8a6516">TENDER / {tender_status} / no submission</text>
  </g>

  <text x="70" y="652" font-family="Arial, sans-serif" font-size="11" font-weight="700" letter-spacing="1.2" fill="#87938e">AUDITABLE OUTPUT AND PROFESSIONAL BOUNDARY</text>

  <rect x="70" y="670" width="610" height="128" rx="12" fill="#eef3f6" stroke="#c9d7df"/>
  <text x="94" y="700" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="#345b70">TRACEABILITY CHAIN</text>
  <text x="94" y="731" font-family="Arial, sans-serif" font-size="17" font-weight="700" fill="#16201d">MSG IDs  -&gt;  REQ IDs  -&gt;  SITE source  -&gt;  {candidate_id}  -&gt;  QTO refs</text>
  <text x="94" y="758" font-family="Arial, sans-serif" font-size="13" fill="#5d6c66">Every derived value keeps its upstream identifier; artifacts exclude timestamps and machine paths.</text>
  <text x="94" y="780" font-family="Arial, sans-serif" font-size="11" fill="#87938e">Evidence: workflow_trace.json + generated SVG + integration regression tests</text>

  <rect x="700" y="670" width="630" height="128" rx="12" fill="#16201d"/>
  <text x="724" y="700" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="#d7a441">HUMAN REVIEW / {review_gate_count} EXPLICIT GATES</text>
  <text x="724" y="731" font-family="Arial, sans-serif" font-size="17" font-weight="700" fill="#ffffff">Architect + engineers + quantity surveyor + client</text>
  <text x="724" y="758" font-family="Arial, sans-serif" font-size="13" fill="#dce7e2">No code inference, authority validation, professional design, whole-building estimate,</text>
  <text x="724" y="780" font-family="Arial, sans-serif" font-size="13" fill="#dce7e2">market pricing, tender comparison, or project-delivery claim.</text>
</svg>
"""
