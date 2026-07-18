import json

import scripts.check_portfolio_site as portfolio_site
from scripts.check_portfolio_site import (
    CASE_STUDY_REQUIREMENTS,
    SITE_ROOT,
    check_case_studies,
    check_case_study_asset_mirrors,
    check_command_copy_contracts,
    check_hero_preload_contracts,
    check_home_evidence_labels,
    check_html_links,
    check_page_accessibility_contracts,
    check_palette_contrast,
    check_public_discovery_contracts,
    check_responsive_media_contracts,
    check_shared_asset_version_contracts,
    check_shared_interaction_contracts,
    check_social_preview_contracts,
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


def test_responsive_visuals_ignore_intrinsic_html_height_hints() -> None:
    assert check_responsive_media_contracts() == []


def test_responsive_media_contract_detects_a_stretched_diagram(tmp_path, monkeypatch) -> None:
    css = portfolio_site.STYLES_PATH.read_text(encoding="utf-8")
    responsive_rule = """.architecture-map img {
  display: block;
  width: 100%;
  height: auto;
  aspect-ratio: 16 / 9;"""
    stretched_rule = """.architecture-map img {
  display: block;
  width: 100%;
  aspect-ratio: 16 / 9;"""
    assert responsive_rule in css
    broken_styles = tmp_path / "styles.css"
    broken_styles.write_text(css.replace(responsive_rule, stretched_rule, 1), encoding="utf-8")
    monkeypatch.setattr(portfolio_site, "STYLES_PATH", broken_styles)

    issues = check_responsive_media_contracts()

    assert any(".architecture-map img must use height: auto" in issue for issue in issues)


def test_shared_site_assets_use_current_content_hashes() -> None:
    assert check_shared_asset_version_contracts() == []


def test_shared_asset_contract_detects_a_stale_stylesheet_hash(tmp_path, monkeypatch) -> None:
    stale_styles = tmp_path / "styles.css"
    stale_styles.write_bytes(portfolio_site.STYLES_PATH.read_bytes() + b"\n")
    monkeypatch.setattr(portfolio_site, "STYLES_PATH", stale_styles)

    issues = check_shared_asset_version_contracts()

    assert len(issues) == len(html_files())
    assert all("stylesheet URL must use the current content hash" in issue for issue in issues)


def test_every_public_page_keeps_accessibility_metadata_and_controls() -> None:
    assert check_page_accessibility_contracts() == []


def test_public_site_keeps_search_share_and_recovery_contracts() -> None:
    assert check_public_discovery_contracts() == []


def test_every_indexable_page_keeps_complete_social_preview_contracts() -> None:
    assert check_social_preview_contracts() == []


def test_social_preview_manifest_detects_stale_page_and_card_hashes(tmp_path, monkeypatch) -> None:
    manifest = json.loads(portfolio_site.SOCIAL_CARD_MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest["pages"]["index.html"]["body_sha256"] = "0" * 64
    manifest["pages"]["index.html"]["card_sha256"] = "0" * 64
    stale_manifest = tmp_path / "social-card-manifest.json"
    stale_manifest.write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(portfolio_site, "SOCIAL_CARD_MANIFEST_PATH", stale_manifest)

    issues = check_social_preview_contracts()

    assert any(
        "visible page body changed after its social preview was captured" in issue
        for issue in issues
    )
    assert any("social-card-home.png: social preview hash is stale" in issue for issue in issues)


def test_social_preview_digest_ignores_shared_script_cache_tokens(tmp_path) -> None:
    page = tmp_path / "page.html"
    page.write_text(
        '<body><main>Visible evidence</main><script src="site.js?v=0123456789ab"></script></body>',
        encoding="utf-8",
    )
    unversioned_page = tmp_path / "unversioned.html"
    unversioned_page.write_text(
        '<body><main>Visible evidence</main><script src="site.js"></script></body>',
        encoding="utf-8",
    )

    assert portfolio_site.social_card_body_digest(page) == portfolio_site.social_card_body_digest(
        unversioned_page
    )


def test_visual_entry_pages_preload_only_their_first_screen_hero() -> None:
    assert check_hero_preload_contracts() == []


def test_shared_site_keeps_keyboard_motion_and_contrast_contracts() -> None:
    assert check_shared_interaction_contracts() == []


def test_every_runnable_site_command_keeps_copy_controls_and_feedback() -> None:
    assert check_command_copy_contracts() == []


def test_shared_palette_keeps_readable_text_contrast() -> None:
    assert check_palette_contrast() == []


def test_every_public_page_uses_the_shared_navigation_script() -> None:
    pages = html_files()

    assert len(pages) == 10
    for page in pages:
        text = page.read_text(encoding="utf-8")
        assert 'class="site-header"' in text
        assert "site.js" in text


def test_case_study_footer_navigation_follows_the_aec_journey() -> None:
    expected_routes = {
        "aec-rag.html": "specification-assistant.html",
        "specification-assistant.html": "massing-explorer.html",
        "massing-explorer.html": "qs-takeoff.html",
        "qs-takeoff.html": "embodied-ai.html",
    }

    for page_name, next_page in expected_routes.items():
        text = (SITE_ROOT / "pages" / page_name).read_text(encoding="utf-8")
        assert f'href="{next_page}"' in text


def test_custom_404_routes_visitors_back_to_primary_evidence() -> None:
    text = (SITE_ROOT / "404.html").read_text(encoding="utf-8")

    assert 'content="noindex, follow"' in text
    assert 'href="https://josiahsutd-stack.github.io/ai-portfolio/"' in text
    assert 'href="https://josiahsutd-stack.github.io/ai-portfolio/pages/aec-rag.html"' in text
    assert 'href="https://josiahsutd-stack.github.io/ai-portfolio/pages/project-guide.html"' in text


def test_legacy_project_guide_route_redirects_without_being_indexed() -> None:
    text = (SITE_ROOT / "pages" / "recruiter-view.html").read_text(encoding="utf-8")

    assert '<meta name="robots" content="noindex, follow" />' in text
    assert '<meta http-equiv="refresh" content="0; url=project-guide.html" />' in text
    assert (
        'rel="canonical" href="https://josiahsutd-stack.github.io/ai-portfolio/pages/project-guide.html"'
        in text
    )
