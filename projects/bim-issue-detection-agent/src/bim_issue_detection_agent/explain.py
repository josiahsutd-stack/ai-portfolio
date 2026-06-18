from __future__ import annotations

from shared.ai import get_llm_provider

from .detector import Issue


def explain_issue(issue: Issue) -> str:
    prompt = (
        "Explain this BIM coordination issue for an architecture QA report.\n"
        f"Issue type: {issue.issue_type}\n"
        f"Room: {issue.room_id}\n"
        f"Severity: {issue.severity}\n"
        f"Message: {issue.message}\n"
        f"Suggested fix: {issue.suggested_fix}"
    )
    return get_llm_provider().generate(prompt, system="You write concise AEC QA explanations.")
