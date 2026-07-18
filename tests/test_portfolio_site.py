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


def test_every_public_page_keeps_accessibility_metadata_and_controls() -> None:
    assert check_page_accessibility_contracts() == []


def test_public_site_keeps_search_share_and_recovery_contracts() -> None:
    assert check_public_discovery_contracts() == []


def test_every_indexable_page_keeps_complete_social_preview_contracts() -> None:
    assert check_social_preview_contracts() == []


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

    assert len(pages) == 9
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
    assert (
        'href="https://josiahsutd-stack.github.io/ai-portfolio/pages/recruiter-view.html"' in text
    )
