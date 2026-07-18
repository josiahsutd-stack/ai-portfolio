from scripts.check_portfolio_site import (
    CASE_STUDY_REQUIREMENTS,
    SITE_ROOT,
    check_case_studies,
    check_case_study_asset_mirrors,
    check_home_evidence_labels,
    check_html_links,
    html_files,
)


def test_home_routes_primary_work_through_visual_case_studies() -> None:
    home = (SITE_ROOT / "index.html").read_text(encoding="utf-8")

    for path in CASE_STUDY_REQUIREMENTS:
        assert f'href="{path}"' in home


def test_case_studies_keep_evidence_and_boundary_contracts() -> None:
    assert check_case_studies() == []
    assert check_case_study_asset_mirrors() == []


def test_site_navigation_and_local_assets_resolve() -> None:
    assert check_html_links() == []
    assert check_home_evidence_labels() == []


def test_every_public_page_uses_the_shared_navigation_script() -> None:
    pages = html_files()

    assert len(pages) == 6
    for page in pages:
        text = page.read_text(encoding="utf-8")
        assert 'class="site-header"' in text
        assert "site.js" in text
