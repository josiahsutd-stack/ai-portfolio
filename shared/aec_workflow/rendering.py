from __future__ import annotations

from html import escape
from typing import Any


def render_workflow_trace_svg(trace: dict[str, Any]) -> str:
    specification = trace["specification_handoff"]
    scenario = trace["scenario_handoff"]
    massing = trace["massing_search"]
    qs = trace["schematic_qs_handoff"]
    selected = massing["selected_candidate"]
    candidate_id = escape(str(selected["candidate"]["candidate_id"]))
    stages = (
        (
            "01",
            "Approved brief",
            f"{specification['approved_requirement_count']} approved requirements",
            (
                f"{specification['mapped_approved_requirement_count']} mapped / "
                f"{specification['retained_approved_requirement_count']} retained"
            ),
        ),
        (
            "02",
            "Sourced scenario",
            f"{scenario['field_count']} explicit fields",
            f"{scenario['source_coverage']:.3f} source coverage",
        ),
        (
            "03",
            "Massing search",
            f"{massing['candidate_count']} candidates",
            (
                f"{massing['feasible_candidate_count']} feasible / "
                f"{massing['approved_storey_eligible_count']} storey-matched"
            ),
        ),
        (
            "04",
            "Selected envelope",
            candidate_id,
            (
                f"utility {selected['utility_score']:.3f} / "
                f"GFA {selected['metrics']['gfa_m2']:.0f} m2"
            ),
        ),
        (
            "05",
            "Schematic QS",
            f"{qs['takeoff_line_count']} quantity lines",
            f"{qs['priced_line_count']} priced / {qs['unpriced_line_count']} unpriced",
        ),
    )
    cards: list[str] = []
    for index, (number, title, primary, secondary) in enumerate(stages):
        x = 40 + index * 226
        cards.append(f"""
  <g transform="translate({x},154)">
    <rect width="198" height="196" rx="6" fill="#ffffff" stroke="#cbd5d1"/>
    <text x="18" y="31" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="#e85d3f">{number}</text>
    <text x="18" y="62" font-family="Arial, sans-serif" font-size="19" font-weight="700" fill="#15231f">{escape(title)}</text>
    <line x1="18" y1="80" x2="180" y2="80" stroke="#dce3df"/>
    <text x="18" y="113" font-family="Arial, sans-serif" font-size="15" font-weight="700" fill="#267d6a">{escape(primary)}</text>
    <text x="18" y="143" font-family="Arial, sans-serif" font-size="12" fill="#5f6e68">{escape(secondary)}</text>
    <text x="18" y="174" font-family="Arial, sans-serif" font-size="11" fill="#7c8984">synthetic / inspectable / local</text>
  </g>""")
        if index < len(stages) - 1:
            arrow_x = x + 202
            cards.append(
                f'<path d="M {arrow_x} 252 H {arrow_x + 19}" stroke="#e7a52e" '
                'stroke-width="3" marker-end="url(#arrow)"/>'
            )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="500" viewBox="0 0 1200 500" role="img" aria-labelledby="title desc">
  <title id="title">Executed AEC design-to-cost workflow trace</title>
  <desc id="desc">Five stages connect approved synthetic requirements to a sourced massing scenario, selected geometry, and a bounded schematic quantity takeoff.</desc>
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#e7a52e"/>
    </marker>
  </defs>
  <rect width="1200" height="500" fill="#f5f3ed"/>
  <rect x="0" y="0" width="1200" height="12" fill="#15231f"/>
  <text x="40" y="62" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#e85d3f">EXECUTED CONTRACT TRACE / SYNTHETIC FIXTURE</text>
  <text x="40" y="103" font-family="Arial, sans-serif" font-size="30" font-weight="700" fill="#15231f">Approved requirements to a reviewable schematic cost input</text>
  <text x="40" y="130" font-family="Arial, sans-serif" font-size="14" fill="#5f6e68">Every handoff records its source. Unapproved, conflicted, missing, or scope-incompatible inputs stop or remain outside automation.</text>
{''.join(cards)}
  <rect x="40" y="386" width="1120" height="72" rx="5" fill="#15231f"/>
  <text x="62" y="417" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#e7a52e">HUMAN REVIEW BOUNDARY</text>
  <text x="62" y="442" font-family="Arial, sans-serif" font-size="13" fill="#ffffff">No code inference, professional design, whole-building estimate, market pricing, tender comparison, or authority validation.</text>
</svg>
"""
