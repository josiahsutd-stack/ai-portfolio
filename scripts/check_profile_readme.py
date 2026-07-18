from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profile-readme.md"
PROFILE_PREVIEW = ROOT / "portfolio-site" / "assets" / "portfolio-home-preview.png"
LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\((?P<target>[^)]+)\)")
REQUIRED_TEXT = (
    "# Josiah Lau | Applied AI Engineer",
    "https://josiahsutd-stack.github.io/ai-portfolio/",
    "https://github.com/josiahsutd-stack/ai-portfolio",
    "https://www.linkedin.com/in/josiah-lau-8041822b6/",
    "mailto:josiahsutd@gmail.com",
    "portfolio-site/assets/portfolio-home-preview.png",
    "AEC Code Compliance RAG",
    "Construction Embodied Agent Simulator",
    "Constraint-Aware Massing Explorer",
    "Evidence Policy",
)
FORBIDDEN_PROFILE_PHRASES = (
    "primary review project",
    "recruiter fast path",
    "interview prep",
    "hiring verdict",
    "would hire",
    "would not hire",
    "start with these",
    "projects to inspect",
    "for a 15-minute",
    "the candidate's",
)


def collect_issues(text: str | None = None) -> list[str]:
    content = PROFILE.read_text(encoding="utf-8") if text is None else text
    issues: list[str] = []

    for required in REQUIRED_TEXT:
        if required not in content:
            issues.append(f"profile-readme.md: missing required content {required!r}")

    for match in LINK_PATTERN.finditer(content):
        target = match.group("target").strip()
        if not target.startswith(("https://", "mailto:")):
            issues.append(f"profile-readme.md: profile links must be absolute, found {target!r}")

    first_link = LINK_PATTERN.search(content)
    if (
        first_link is None
        or first_link.group("target").strip() != "https://josiahsutd-stack.github.io/ai-portfolio/"
    ):
        issues.append("profile-readme.md: visual portfolio must be the first link")

    lowered = content.lower()
    for phrase in FORBIDDEN_PROFILE_PHRASES:
        if phrase in lowered:
            issues.append(f"profile-readme.md: candidate-facing meta-language {phrase!r}")

    image_line = next(
        (
            index
            for index, line in enumerate(content.splitlines(), start=1)
            if line.startswith("[![")
        ),
        None,
    )
    if image_line is None or image_line > 12:
        issues.append("profile-readme.md: portfolio preview must appear by line 12")

    if not PROFILE_PREVIEW.is_file():
        issues.append("profile-readme.md: local portfolio preview image is missing")

    if len(content.splitlines()) > 90:
        issues.append("profile-readme.md: profile entry point exceeds 90 lines")
    return issues


def main() -> None:
    issues = collect_issues()
    if issues:
        print("Profile README check failed:")
        for issue in issues:
            print(f"- {issue}")
        sys.exit(1)
    link_count = len(LINK_PATTERN.findall(PROFILE.read_text(encoding="utf-8")))
    print(f"Profile README check passed with {link_count} absolute links.")


if __name__ == "__main__":
    main()
