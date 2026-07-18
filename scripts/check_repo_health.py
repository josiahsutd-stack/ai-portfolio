from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PROJECTS_DIR = ROOT / "projects"
EXPERIMENTS_DIR = ROOT / "experiments"
REQUIRED_DOCS = [
    "README.md",
    "EVIDENCE_COVERAGE_AUDIT.md",
    "profile-readme.md",
    "ENGINEERING_REVIEW_LOG.md",
    "docs/troubleshooting.md",
    "docs/how-to-review-this-portfolio.md",
    "docs/technical-review-guide.md",
    "docs/skills-matrix.md",
    "docs/role-to-project-map.md",
    "docs/REVIEWER_GUIDE.md",
    "docs/ENGINEERING_DECISIONS.md",
    "docs/CLAIMS_POLICY.md",
    "docs/EVIDENCE_LEDGER.md",
    "docs/evidence_claims.yml",
    "docs/ARCHITECTURE_BACKGROUND.md",
    "docs/adr/0001-local-first-synthetic-data.md",
    "docs/adr/0002-aec-rag-as-flagship.md",
    "docs/adr/0003-mock-provider-boundaries.md",
    "docs/adr/0004-evaluation-over-claims.md",
    "docs/adr/0005-flagship-depth-over-project-breadth.md",
    "docs/adr/0007-executable-aec-integration.md",
    "projects/projects.yml",
    "experiments/README.md",
    "integrations/README.md",
    "integrations/aec-design-to-cost/README.md",
    "integrations/aec-design-to-cost/ARCHITECTURE.md",
    "integrations/aec-design-to-cost/EVAL.md",
    "integrations/aec-design-to-cost/LIMITATIONS.md",
    "integrations/aec-design-to-cost/sample_data/synthetic_workflow_case.json",
    ".github/workflows/ci.yml",
    "experiments/local-text-classification-lab/EVAL.md",
    "experiments/local-text-classification-lab/sample_data/uci_sms_subset_manifest.json",
    "experiments/local-text-classification-lab/scripts/build_uci_sms_subset.py",
]
FORBIDDEN_PUBLIC_DOCS = [
    "FINAL_HIRING_MANAGER_REVIEW.md",
    "docs/AUTHENTICITY_AND_OWNERSHIP.md",
    "PORTFOLIO_REVIEW_ROUNDS.md",
]
REQUIRED_README_PATTERNS = {
    "demo command": r"streamlit run (projects|experiments)/.+/app\.py",
    "tests": r"## Tests|pytest tests/|python -m pytest tests/",
    "limitations": r"## Limitations",
    "next steps": r"## (Credible Next Steps|Deployment-Relevant Extensions|Next Steps)",
}
REQUIRED_ROOT_README_PATTERNS = {
    "selected work": r"## Selected Work",
    "plain-language evidence column": r"Evidence in plain language",
    "single reviewer command": r"python scripts/reviewer_check\.py",
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
    "cross-project integration command": r"python integrations/aec-design-to-cost/run_workflow\.py",
}
REQUIRED_WORKFLOW_PATTERNS = {
    "push trigger": r"(?m)^\s*push:\s*$",
    "pull-request trigger": r"(?m)^\s*pull_request:\s*$",
    "manual trigger": r"(?m)^\s*workflow_dispatch:\s*$",
    "main branch trigger": r'(?m)^\s*branches:\s*\["main"\]\s*$',
    "read-only contents permission": r"(?m)^\s*contents:\s*read\s*$",
    "bounded runtime": r"(?m)^\s*timeout-minutes:\s*20\s*$",
    "current checkout action": r"actions/checkout@v6",
    "current Python setup action": r"actions/setup-python@v6",
    "dependency cache": r"(?m)^\s*cache:\s*pip\s*$",
    "repository verifier": r"python scripts/verify\.py",
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
    "deep learning",
    "fine-tune",
    "fine-tuning",
    "reinforcement learning",
    "state-of-the-art",
    "platform",
    "vlm",
}
RETIRED_EXPERIMENT_SLUGS = {
    "agentic-research-ops-assistant",
    "bim-issue-detection-agent",
    "building-energy-ml-pipeline",
    "construction-robot-task-planner",
    "deep-learning-vision-lab",
    "fine-tuning-lora-lab",
    "llm-evals-guardrails-platform",
    "mlops-model-serving-monitoring",
    "multimodal-vlm-visual-qa",
    "real-model-finetune-lab",
    "recommender-system-ranking-engine",
    "reinforcement-learning-portfolio",
    "site-robot-safety-monitor",
    "time-series-anomaly-forecasting",
}


def contains_files(path: Path) -> bool:
    return any(child.is_file() for child in path.rglob("*"))


def project_dirs() -> list[Path]:
    directories: list[Path] = []
    for root in (PROJECTS_DIR, EXPERIMENTS_DIR):
        directories.extend(
            path for path in root.iterdir() if path.is_dir() and contains_files(path)
        )
    return sorted(directories, key=lambda path: path.name)


def check_required_docs() -> list[str]:
    return [f"missing required doc: {doc}" for doc in REQUIRED_DOCS if not (ROOT / doc).exists()]


def check_forbidden_public_docs() -> list[str]:
    return [
        f"obsolete public doc must remain removed: {doc}"
        for doc in FORBIDDEN_PUBLIC_DOCS
        if (ROOT / doc).exists()
    ]


def check_root_readme() -> list[str]:
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8") if readme.exists() else ""
    issues = [
        f"README.md: missing {label}"
        for label, pattern in REQUIRED_ROOT_README_PATTERNS.items()
        if not re.search(pattern, text, flags=re.IGNORECASE)
    ]
    return issues


def check_verification_workflow() -> list[str]:
    workflow = ROOT / ".github" / "workflows" / "ci.yml"
    text = workflow.read_text(encoding="utf-8") if workflow.exists() else ""
    issues = [
        f".github/workflows/ci.yml: missing {label}"
        for label, pattern in REQUIRED_WORKFLOW_PATTERNS.items()
        if not re.search(pattern, text)
    ]
    duplicate = ROOT / ".github" / "workflows" / "verify.yml"
    if duplicate.exists():
        issues.append(".github/workflows/verify.yml: duplicate verifier workflow must stay removed")
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
        normalized_slug = slug.lower().replace("-", " ")
        for phrase in INFLATED_PROJECT_NAME_PHRASES:
            if phrase in lowered_name:
                issues.append(f"{slug}: public name contains inflated capability phrase `{phrase}`")
            if phrase in normalized_slug:
                issues.append(f"{slug}: public slug contains inflated capability phrase `{phrase}`")

        readme_path = ROOT / str(row.get("readme_path", ""))
        expected_root = EXPERIMENTS_DIR if status == "experiment" else PROJECTS_DIR
        expected_readme = expected_root / slug / "README.md"
        if readme_path != expected_readme:
            expected_relative = expected_readme.relative_to(ROOT).as_posix()
            issues.append(f"{slug}: readme_path must be `{expected_relative}`")
        elif readme_path.exists():
            lines = readme_path.read_text(encoding="utf-8").splitlines()
            first_line = lines[0] if lines else ""
            if first_line != f"# {name}":
                shown_title = first_line or "<empty>"
                issues.append(f"{slug}: README title `{shown_title}` does not match `{name}`")

    directory_slugs = {path.name for path in project_dirs()}
    if len(slugs) != len(set(slugs)):
        issues.append("projects/projects.yml: duplicate project slug")
    restored_retired_experiments = sorted(set(slugs) & RETIRED_EXPERIMENT_SLUGS)
    if restored_retired_experiments:
        issues.append(
            "projects/projects.yml: retired experiment slugs must stay absent: "
            + ", ".join(restored_retired_experiments)
        )
    if set(slugs) != directory_slugs:
        missing_rows = sorted(directory_slugs - set(slugs))
        unknown_rows = sorted(set(slugs) - directory_slugs)
        if missing_rows:
            issues.append(
                f"manifest missing project or experiment directories: {', '.join(missing_rows)}"
            )
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
        + check_forbidden_public_docs()
        + check_root_readme()
        + check_verification_workflow()
        + check_project_manifest()
        + check_project_readmes()
        + check_generic_language()
    )
    if issues:
        print("Repo health check failed:")
        for issue in issues:
            print(f"- {issue}")
        sys.exit(1)
    directories = project_dirs()
    selected_count = sum(path.parent == PROJECTS_DIR for path in directories)
    experiment_count = sum(path.parent == EXPERIMENTS_DIR for path in directories)
    print(
        "Repo health check passed for "
        f"{selected_count} selected projects and {experiment_count} experiments."
    )


if __name__ == "__main__":
    main()
