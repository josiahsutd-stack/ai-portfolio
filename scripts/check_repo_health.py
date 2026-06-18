from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECTS_DIR = ROOT / "projects"
REQUIRED_DOCS = [
    "README.md",
    "profile-readme.md",
    "docs/repo-audit.md",
    "docs/troubleshooting.md",
    "docs/how-to-review-this-portfolio.md",
    "docs/interview-prep.md",
    "docs/skills-matrix.md",
    "docs/role-to-project-map.md",
    "docs/resume-project-bullets.md",
    "docs/recruiter-snippets.md",
    "docs/project-roadmap.md",
    "projects/projects.yml",
]
REQUIRED_README_PATTERNS = {
    "demo command": r"streamlit run projects/.+/app\.py",
    "what proves": r"## What This Proves [Tt]o Employers|## What It Proves to Employers",
    "limitations": r"## Limitations",
    "engineering notes": r"## Engineering Notes",
    "interview talking points": r"## Interview Talking Points",
}
GENERIC_PHRASES = [
    "leveraging cutting-edge",
    "revolutionizing",
    "seamlessly integrates",
    "robust and scalable solution",
    "powered by advanced ai",
    "state-of-the-art",
    "production-ready",
]


def project_dirs() -> list[Path]:
    return sorted(path for path in PROJECTS_DIR.iterdir() if path.is_dir())


def check_required_docs() -> list[str]:
    return [f"missing required doc: {doc}" for doc in REQUIRED_DOCS if not (ROOT / doc).exists()]


def check_project_readmes() -> list[str]:
    issues: list[str] = []
    for project in project_dirs():
        readme = project / "README.md"
        if not readme.exists():
            issues.append(f"{project.name}: missing README.md")
            continue
        text = readme.read_text(encoding="utf-8")
        for label, pattern in REQUIRED_README_PATTERNS.items():
            if not re.search(pattern, text, flags=re.IGNORECASE):
                issues.append(f"{project.name}: missing {label}")
        if not (project / "app.py").exists() and "documented entrypoint" not in text.lower():
            issues.append(f"{project.name}: missing app.py or documented entrypoint")
        if not (project / "sample_data").exists():
            issues.append(f"{project.name}: missing sample_data directory")
    return issues


def check_generic_language() -> list[str]:
    issues: list[str] = []
    markdown_files = list(ROOT.glob("*.md")) + list((ROOT / "docs").glob("*.md"))
    markdown_files += [
        project / "README.md" for project in project_dirs() if (project / "README.md").exists()
    ]
    for path in markdown_files:
        text = path.read_text(encoding="utf-8").lower()
        for phrase in GENERIC_PHRASES:
            if phrase in text:
                issues.append(f"{path.relative_to(ROOT)}: generic/overclaim phrase `{phrase}`")
    return issues


def main() -> None:
    issues = check_required_docs() + check_project_readmes() + check_generic_language()
    if issues:
        print("Repo health check failed:")
        for issue in issues:
            print(f"- {issue}")
        sys.exit(1)
    print(f"Repo health check passed for {len(project_dirs())} projects.")


if __name__ == "__main__":
    main()
