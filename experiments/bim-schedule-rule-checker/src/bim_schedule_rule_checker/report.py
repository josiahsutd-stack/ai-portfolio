from __future__ import annotations

from collections import Counter

from shared.utils import markdown_table

from .detector import Issue


def issue_report_markdown(issues: list[Issue]) -> str:
    if not issues:
        return "# BIM Issue Report\n\nNo issues detected in the supplied demo schedule."
    severity_counts = Counter(issue.severity for issue in issues)
    rows = [issue.to_dict() for issue in issues]
    summary = ", ".join(
        f"{count} {severity}" for severity, count in sorted(severity_counts.items())
    )
    return (
        "# BIM Issue Report\n\n"
        "Synthetic/demo data. Review all findings with a qualified project team.\n\n"
        f"## Summary\n\nDetected {len(issues)} issue(s): {summary}.\n\n"
        "## Issue Register\n\n"
        f"{markdown_table(rows)}\n"
    )
