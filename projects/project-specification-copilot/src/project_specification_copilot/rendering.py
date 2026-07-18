from __future__ import annotations

from html import escape

from .models import ProjectSnapshot, SpecificationDraft

ROLE_COLORS = {
    "client": "#e85d3f",
    "architect": "#2f7d6d",
    "structural_engineer": "#5b6da8",
    "mep_engineer": "#d99a2b",
    "quantity_surveyor": "#805a9d",
    "project_manager": "#26708f",
    "contractor": "#6f736f",
}


def _short(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "..."


def render_specification_trace_svg(snapshot: ProjectSnapshot, draft: SpecificationDraft) -> str:
    messages = snapshot.messages[:6]
    requirements = [
        requirement for requirement in snapshot.requirements if requirement.status != "superseded"
    ][:7]
    clauses = draft.clauses[:6]
    message_rows = []
    for index, message in enumerate(messages):
        y = 138 + index * 62
        color = ROLE_COLORS.get(message.role, "#6f736f")
        message_rows.append(
            f'<circle cx="52" cy="{y + 4}" r="9" fill="{color}"/>'
            f'<text x="72" y="{y}" font-size="11" font-weight="700" fill="#17231f">{escape(message.message_id)} · {escape(message.role.replace("_", " ").title())}</text>'
            f'<text x="72" y="{y + 22}" font-size="11" fill="#59665f">{escape(_short(message.text, 46))}</text>'
        )
    requirement_rows = []
    for index, requirement in enumerate(requirements):
        y = 132 + index * 53
        status_color = "#2f7d6d" if requirement.status == "approved" else "#d99a2b"
        requirement_rows.append(
            f'<rect x="427" y="{y - 20}" width="312" height="42" rx="4" fill="#ffffff" stroke="#d8ddd8"/>'
            f'<rect x="427" y="{y - 20}" width="7" height="42" fill="{status_color}"/>'
            f'<text x="447" y="{y - 2}" font-size="11" font-weight="700" fill="#17231f">{escape(requirement.requirement_id)} · {escape(requirement.statement)}</text>'
            f'<text x="447" y="{y + 14}" font-size="10" fill="#66736c">{escape(requirement.status.upper())} · source {escape(", ".join(requirement.source_message_ids))}</text>'
        )
    clause_rows = []
    for index, clause in enumerate(clauses):
        y = 132 + index * 57
        clause_rows.append(
            f'<text x="825" y="{y - 4}" font-size="11" font-weight="700" fill="#2f7d6d">{escape(clause.clause_id)} · {escape(clause.section)}</text>'
            f'<text x="825" y="{y + 15}" font-size="11" fill="#17231f">{escape(_short(clause.text, 48))}</text>'
            f'<line x1="825" y1="{y + 27}" x2="1150" y2="{y + 27}" stroke="#d8ddd8"/>'
        )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="590" viewBox="0 0 1200 590" role="img" aria-labelledby="title desc">
  <title id="title">Role-aware project communication and specification trace</title>
  <desc id="desc">Synthetic conversation messages linked to extracted requirements and approved specification clauses.</desc>
  <rect width="1200" height="590" fill="#f4f1e9"/>
  <text x="34" y="38" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#e85d3f">PROJECT COMMUNICATION AND SPECIFICATION ASSISTANT · SYNTHETIC TRACE</text>
  <text x="34" y="72" font-family="Arial, sans-serif" font-size="29" font-weight="700" fill="#17231f">Conversation evidence becomes a reviewable draft</text>
  <text x="34" y="99" font-family="Arial, sans-serif" font-size="12" fill="#66736c">No approved clause without a source message and authorized role action.</text>
  <line x1="390" y1="116" x2="390" y2="530" stroke="#cbd2cc"/>
  <line x1="780" y1="116" x2="780" y2="530" stroke="#cbd2cc"/>
  <text x="34" y="126" font-family="Arial, sans-serif" font-size="11" font-weight="700" fill="#66736c">01 · ROLE-TAGGED MESSAGES</text>
  <text x="427" y="102" font-family="Arial, sans-serif" font-size="11" font-weight="700" fill="#66736c">02 · REQUIREMENT LEDGER</text>
  <text x="825" y="102" font-family="Arial, sans-serif" font-size="11" font-weight="700" fill="#66736c">03 · APPROVED DRAFT CLAUSES</text>
  <g font-family="Arial, sans-serif">{''.join(message_rows)}{''.join(requirement_rows)}{''.join(clause_rows)}</g>
  <rect x="34" y="536" width="1116" height="34" rx="3" fill="#17231f"/>
  <text x="52" y="558" font-family="Arial, sans-serif" font-size="11" fill="#ffffff">Status: {escape(draft.status)} · Open conflicts: {len(draft.open_conflict_ids)} · Awaiting approval: {len(draft.unapproved_requirement_ids)} · Draft version: {escape(draft.version)}</text>
</svg>"""
