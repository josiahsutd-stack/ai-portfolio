from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

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
    "docs/EVIDENCE_LEDGER.md",
    "docs/evidence_claims.yml",
    "docs/ARCHITECTURE_BACKGROUND.md",
    "docs/adr/0001-local-first-synthetic-data.md",
    "docs/adr/0002-aec-rag-as-flagship.md",
    "docs/adr/0003-mock-provider-boundaries.md",
    "docs/adr/0004-evaluation-over-claims.md",
    "docs/adr/0005-flagship-depth-over-project-breadth.md",
    "projects/projects.yml",
    "projects/real-model-finetune-lab/EVAL.md",
    "projects/real-model-finetune-lab/sample_data/uci_sms_subset_manifest.json",
    "projects/real-model-finetune-lab/scripts/build_uci_sms_subset.py",
]
REQUIRED_README_PATTERNS = {
    "demo command": r"streamlit run projects/.+/app\.py",
    "tests": r"## Tests|pytest tests/|python -m pytest tests/",
    "limitations": r"## Limitations",
    "next steps": r"## (Credible Next Steps|Deployment-Relevant Extensions|Next Steps)",
}
REQUIRED_ROOT_README_PATTERNS = {
    "selected work": r"## Selected Work",
    "measured result column": r"Current result",
    "quick evidence command": r"python projects/aec-code-compliance-rag/scripts/evaluate_retrieval\.py",
    "local run path": r"## Run Locally",
    "flagship project": r"## Flagship Project",
    "system overview": r"## System Overview",
    "architecture background": r"## Architecture Background",
    "generated visual boundary": r"not a simulator screenshot or hardware claim",
    "architecture provenance link": r"docs/ARCHITECTURE_BACKGROUND\.md",
    "evidence labels": r"## Evidence Labels",
    "limitations link": r"docs/SCOPE_AND_LIMITATIONS\.md",
    "evidence ledger link": r"docs/EVIDENCE_LEDGER\.md",
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
    "designed for technical review",
    "candidate's applied ai profile",
    "without pretending every project is a flagship",
    "## reviewer signal",
    "## engineering notes",
    "## technical review discussion points",
    "reviewers can",
]
ALLOWED_PROJECT_STATUSES = {"flagship", "primary", "supporting", "experiment"}
REQUIRED_MANIFEST_FIELDS = {
    "name",
    "slug",
    "category",
    "skill_area",
    "flagship",
    "demo_command",
    "test_command",
    "tech_stack",
    "summary",
    "skills",
    "status",
    "data_mode",
    "implementation_mode",
    "boundary",
    "readme_path",
}
INFLATED_PROJECT_NAME_PHRASES = {
    "fine-tune",
    "fine-tuning",
    "reinforcement learning",
    "state-of-the-art",
    "platform",
    "vlm",
}


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


def check_project_manifest() -> list[str]:
    manifest_path = ROOT / "projects" / "projects.yml"
    if not manifest_path.exists():
        return ["missing required doc: projects/projects.yml"]
    try:
        payload = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [f"projects/projects.yml: invalid YAML: {exc}"]
    rows = payload.get("projects") if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        return ["projects/projects.yml: top-level `projects` must be a list"]

    issues: list[str] = []
    slugs: list[str] = []
    flagship_count = 0
    non_experiment_count = 0
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            issues.append(f"projects/projects.yml: row {index} must be a mapping")
            continue
        missing = sorted(REQUIRED_MANIFEST_FIELDS - row.keys())
        slug = str(row.get("slug", f"row-{index}"))
        if missing:
            issues.append(f"{slug}: manifest missing fields: {', '.join(missing)}")
        slugs.append(slug)
        status = row.get("status")
        if status not in ALLOWED_PROJECT_STATUSES:
            issues.append(f"{slug}: unsupported status `{status}`")
        if status != "experiment":
            non_experiment_count += 1
        is_flagship = row.get("flagship") is True
        flagship_count += int(is_flagship)
        if is_flagship != (status == "flagship"):
            issues.append(f"{slug}: `flagship` boolean and status disagree")

        name = str(row.get("name", ""))
        lowered_name = name.lower()
        for phrase in INFLATED_PROJECT_NAME_PHRASES:
            if phrase in lowered_name:
                issues.append(f"{slug}: public name contains inflated capability phrase `{phrase}`")

        readme_path = ROOT / str(row.get("readme_path", ""))
        expected_readme = ROOT / "projects" / slug / "README.md"
        if readme_path != expected_readme:
            issues.append(f"{slug}: readme_path must be `projects/{slug}/README.md`")
        elif readme_path.exists():
            lines = readme_path.read_text(encoding="utf-8").splitlines()
            first_line = lines[0] if lines else ""
            if first_line != f"# {name}":
                shown_title = first_line or "<empty>"
                issues.append(f"{slug}: README title `{shown_title}` does not match `{name}`")

    directory_slugs = {path.name for path in project_dirs()}
    if len(slugs) != len(set(slugs)):
        issues.append("projects/projects.yml: duplicate project slug")
    if set(slugs) != directory_slugs:
        missing_rows = sorted(directory_slugs - set(slugs))
        unknown_rows = sorted(set(slugs) - directory_slugs)
        if missing_rows:
            issues.append(f"manifest missing project directories: {', '.join(missing_rows)}")
        if unknown_rows:
            issues.append(f"manifest has unknown project directories: {', '.join(unknown_rows)}")
    if flagship_count != 1:
        issues.append(f"manifest must contain exactly one flagship; found {flagship_count}")
    if non_experiment_count > 5:
        issues.append(
            f"manifest has {non_experiment_count} projects above experiment tier; maximum is 5"
        )
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
        + check_project_manifest()
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
