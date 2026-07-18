import json

import scripts.check_profile_readme as profile_readme
from scripts.check_profile_readme import (
    GITHUB_REPOSITORY_PREVIEW,
    collect_issues,
    jpeg_dimensions,
)


def test_profile_readme_is_self_contained_and_recruiter_facing() -> None:
    assert collect_issues() == []


def test_repository_social_preview_matches_github_upload_contract() -> None:
    assert jpeg_dimensions(GITHUB_REPOSITORY_PREVIEW) == (1280, 640)
    assert GITHUB_REPOSITORY_PREVIEW.stat().st_size < 1_000_000


def test_repository_social_preview_tracks_the_current_homepage_hero() -> None:
    assert profile_readme.repository_preview_manifest_issues() == []


def test_repository_social_preview_detects_a_stale_hero_capture(tmp_path, monkeypatch) -> None:
    manifest = json.loads(
        profile_readme.GITHUB_REPOSITORY_PREVIEW_MANIFEST.read_text(encoding="utf-8")
    )
    manifest["source_sha256"] = "0" * 64
    stale_manifest = tmp_path / "repository-preview-manifest.json"
    stale_manifest.write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(profile_readme, "GITHUB_REPOSITORY_PREVIEW_MANIFEST", stale_manifest)

    issues = profile_readme.repository_preview_manifest_issues()

    assert any("homepage hero changed" in issue for issue in issues)


def test_profile_readme_rejects_relative_links() -> None:
    text = "\n".join(
        [
            "# Josiah Lau | Applied AI Engineer",
            "[Visual portfolio](docs/portfolio.html)",
            "AEC Code Compliance RAG",
        ]
    )

    issues = collect_issues(text)

    assert any("links must be absolute" in issue for issue in issues)


def test_profile_readme_rejects_review_process_meta_language() -> None:
    issues = collect_issues("# Josiah Lau\n\nStart with these projects to inspect.")

    assert any("candidate-facing meta-language" in issue for issue in issues)


def test_profile_readme_requires_visual_portfolio_as_first_link() -> None:
    text = "\n".join(
        [
            "# Josiah Lau | Applied AI Engineer",
            "[GitHub](https://github.com/josiahsutd-stack)",
            "[Visual portfolio](https://josiahsutd-stack.github.io/ai-portfolio/)",
        ]
    )

    issues = collect_issues(text)

    assert "profile-readme.md: visual portfolio must be the first link" in issues
