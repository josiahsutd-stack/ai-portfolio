from scripts.check_profile_readme import collect_issues


def test_profile_readme_is_self_contained_and_recruiter_facing() -> None:
    assert collect_issues() == []


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
