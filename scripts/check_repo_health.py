from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECTS_DIR = ROOT / "projects"
REQUIRED_DOCS = [
    "README.md",
    "profile-readme.md",
    "docs/troubleshooting.md",
    "docs/how-to-review-this-portfolio.md",
    "docs/technical-review-guide.md",
    "docs/skills-matrix.md",
    "docs/role-to-project-map.md",
    "docs/REVIEWER_GUIDE.md",
    "docs/AUTHENTICITY_AND_OWNERSHIP.md",
    "docs/CLAIMS_POLICY.md",
    "docs/adr/0001-local-first-synthetic-data.md",
    "docs/adr/0002-aec-rag-as-flagship.md",
    "docs/adr/0003-mock-provider-boundaries.md",
    "docs/adr/0004-evaluation-over-claims.md",
    "docs/adr/0005-flagship-depth-over-project-breadth.md",
    "projects/projects.yml",
]
REQUIRED_README_PATTERNS = {
    "demo command": r"streamlit run projects/.+/app\.py",
    "reviewer signal": r"## Reviewer Signal",
    "limitations": r"## Limitations",
    "engineering notes": r"## Engineering Notes",
    "technical review discussion points": r"## Technical Review Discussion Points",
}
REQUIRED_ROOT_README_PATTERNS = {
    "recruiter fast path": r"## Recruiter Fast Path",
    "measured result column": r"Current local result",
    "quick evidence command": r"python projects/aec-code-compliance-rag/scripts/evaluate_retrieval\.py",
    "local run path": r"## Run Evidence Locally",
    "flagship evidence": r"## Flagship Evidence",
    "evidence labels": r"## Evidence Labels",
    "limitations link": r"docs/SCOPE_AND_LIMITATIONS\.md",
}
GENERIC_PHRASES = [
    "leveraging cutting-edge",
    "revolutionizing",
    "seamlessly integrates",
    "robust and scalable solution",
    "powered by advanced ai",
    "state-of-the-art",
    "production-ready",
    "production-grade",
]


def project_dirs() -> list[Path]:
    return sorted(path for path in PROJECTS_DIR.iterdir() if path.is_dir())


def check_required_docs() -> list[str]:
    return [f"missing required doc: {doc}" for doc in REQUIRED_DOCS if not (ROOT / doc).exists()]


def check_root_readme() -> list[str]:
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8") if readme.exists() else ""
    issues = [
        f"README.md: missing {label}"
        for label, pattern in REQUIRED_ROOT_README_PATTERNS.items()
        if not re.search(pattern, text, flags=re.IGNORECASE)
    ]
    return issues


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
        if path.relative_to(ROOT).as_posix() == "docs/CLAIMS_POLICY.md":
            continue
        text = path.read_text(encoding="utf-8").lower()
        for phrase in GENERIC_PHRASES:
            if phrase in text:
                issues.append(f"{path.relative_to(ROOT)}: generic/overclaim phrase `{phrase}`")
    return issues


def main() -> None:
    issues = (
        check_required_docs()
        + check_root_readme()
        + check_project_readmes()
        + check_generic_language()
    )
    if issues:
        print("Repo health check failed:")
        for issue in issues:
            print(f"- {issue}")
        sys.exit(1)
    print(f"Repo health check passed for {len(project_dirs())} projects.")


if __name__ == "__main__":
    main()
