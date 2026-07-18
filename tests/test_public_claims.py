from scripts.check_claims import ROOT, collect_issues, line_issues, public_text_files
from scripts.check_repo_health import RETIRED_EXPERIMENT_SLUGS, check_forbidden_public_docs


def test_claim_scan_includes_static_site_and_integration_docs() -> None:
    relative_paths = {path.relative_to(ROOT).as_posix() for path in public_text_files()}

    assert "portfolio-site/index.html" in relative_paths
    assert "integrations/aec-design-to-cost/README.md" in relative_paths


def test_claim_scan_rejects_candidate_authored_numeric_score() -> None:
    issues = line_issues(
        ROOT / "README.md",
        1,
        "Overall junior applied interview readiness: 8.7/10.",
    )

    assert any("numeric portfolio score" in issue for issue in issues)
    assert any("interview readiness" in issue for issue in issues)


def test_claim_scan_rejects_simulated_hiring_verdict() -> None:
    issues = line_issues(
        ROOT / "README.md",
        1,
        "Brutally honest score: I would hire this candidate.",
    )

    assert any("brutally honest score" in issue for issue in issues)
    assert any("i would hire" in issue for issue in issues)


def test_current_public_surfaces_pass_claim_scan() -> None:
    assert collect_issues() == []


def test_obsolete_hiring_verdict_document_remains_removed() -> None:
    assert check_forbidden_public_docs() == []


def test_claim_scan_rejects_deprecated_project_name() -> None:
    issues = line_issues(
        ROOT / "profile-readme.md",
        1,
        "Project Brief and Specification Copilot",
    )

    assert any("deprecated public project name" in issue for issue in issues)


def test_claim_scan_rejects_retired_research_workflow_title() -> None:
    issues = line_issues(
        ROOT / "profile-readme.md",
        1,
        "Deterministic Research Workflow Assistant",
    )

    assert any("deprecated public project name" in issue for issue in issues)


def test_removed_or_renamed_experiment_slugs_stay_absent() -> None:
    expected = {
        "agentic-research-ops-assistant",
        "bim-issue-detection-agent",
        "construction-robot-task-planner",
        "deep-learning-vision-lab",
        "llm-evals-guardrails-platform",
        "mlops-model-serving-monitoring",
        "multimodal-vlm-visual-qa",
        "real-model-finetune-lab",
        "recommender-system-ranking-engine",
        "reinforcement-learning-portfolio",
        "site-robot-safety-monitor",
        "time-series-anomaly-forecasting",
    }

    assert expected <= RETIRED_EXPERIMENT_SLUGS
