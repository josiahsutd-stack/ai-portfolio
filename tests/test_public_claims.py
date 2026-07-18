from scripts.check_claims import ROOT, collect_issues, line_issues, public_text_files
from scripts.check_repo_health import check_forbidden_public_docs


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
