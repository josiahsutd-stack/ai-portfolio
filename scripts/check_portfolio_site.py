from __future__ import annotations

import json
import re
import struct
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
SITE_ROOT = ROOT / "portfolio-site"
PUBLIC_BASE_URL = "https://josiahsutd-stack.github.io/ai-portfolio/"
SOCIAL_SITE_NAME = "Josiah Lau | Applied AI Engineering"
SOCIAL_LOCALE = "en_SG"
PLACEHOLDER_PATTERNS = [
    "your-username",
    "your-name",
    "your.email",
    "example.com",
]
URL_PATTERN = re.compile(r"url\((?P<quote>['\"]?)(?P<path>.*?)(?P=quote)\)")
CSS_VARIABLE_PATTERN = re.compile(r"--(?P<name>[a-z0-9-]+):\s*(?P<value>#[0-9a-fA-F]{6})")
JSON_LD_PATTERN = re.compile(
    r'<script\s+type="application/ld\+json">\s*(?P<payload>.*?)\s*</script>',
    re.DOTALL,
)
REQUIRED_CONTRAST_PAIRS = [
    ("clay", "white", 4.5),
    ("clay", "paper", 4.5),
    ("gold", "ink", 4.5),
    ("muted", "white", 4.5),
    ("muted", "paper", 4.5),
]
REQUIRED_HOME_ASSETS = [
    "assets/favicon.svg",
    "assets/applied-ai-construction-hero.webp",
    "assets/embodied-ai-concept.webp",
    "assets/architecture-ai-transfer-map.webp",
    "assets/bamboo-factory-thesis.webp",
    "assets/tideline-commons-concept.webp",
    "assets/monsoon-works-concept.webp",
    "assets/Josiah_Lau_Applied_AI_Portfolio_Brief.pdf",
]
HERO_PRELOAD_REQUIREMENTS = {
    "index.html": ("assets/applied-ai-construction-hero.webp", "image/webp"),
    "pages/aec-rag.html": ("../assets/aec-rag-demo.png", "image/png"),
    "pages/embodied-ai.html": ("../assets/embodied-ai-concept.webp", "image/webp"),
    "pages/massing-explorer.html": ("../assets/massing-explorer-demo.png", "image/png"),
    "pages/specification-assistant.html": (
        "../assets/specification-copilot-demo.png",
        "image/png",
    ),
    "pages/qs-takeoff.html": ("../assets/qs-takeoff-tender-demo.png", "image/png"),
}
SOCIAL_CARD_REQUIREMENTS = {
    "index.html": (
        "assets/social-card-home.png",
        "Josiah Lau applied AI engineering portfolio hero for architecture and construction",
    ),
    "pages/aec-rag.html": (
        "assets/social-card-aec-rag.png",
        "AEC Code Compliance RAG case-study hero with local interface evidence",
    ),
    "pages/embodied-ai.html": (
        "assets/social-card-embodied-ai.png",
        "Construction Embodied Agent Simulator case-study hero",
    ),
    "pages/massing-explorer.html": (
        "assets/social-card-massing-explorer.png",
        "Constraint-Aware Massing Explorer case-study hero with generated option interface",
    ),
    "pages/specification-assistant.html": (
        "assets/social-card-specification-assistant.png",
        "Communication and Specification Assistant case-study hero with requirement interface",
    ),
    "pages/qs-takeoff.html": (
        "assets/social-card-qs-takeoff.png",
        "QS Takeoff and Tender Analysis case-study hero with measured quantity interface",
    ),
    "pages/project-guide.html": (
        "assets/social-card-project-guide.png",
        "Josiah Lau project guide showing applied AI work organized by role",
    ),
    "pages/skills-matrix.html": (
        "assets/social-card-skills-matrix.png",
        "Josiah Lau skills matrix linking capabilities to projects and evidence",
    ),
}
REQUIRED_HOME_BOUNDARIES = [
    "generated portfolio concept image / not hardware evidence",
    "not a simulator screenshot or hardware evidence",
    "ai-assisted visualization anchored to original drawings",
    "not commissioned or built",
    "not structural design or a fabrication package",
]
REQUIRED_HOME_SECTIONS = [
    "focused experiments",
    "remain experiments rather than first-screen portfolio claims",
    "one-command technical check",
    "python scripts/reviewer_check.py",
    "five implemented systems across one aec decision journey",
    'id="capabilities"',
    'id="directory"',
    'id="contact"',
    "evidence-card__visual",
    "mailto:josiahsutd@gmail.com",
    'aria-expanded="false"',
    "scroll-progress",
    "workflow-proof--system",
    'property="og:image"',
    'rel="canonical"',
    'href="pages/aec-rag.html"',
    'href="pages/embodied-ai.html"',
    'href="pages/massing-explorer.html"',
    'href="pages/specification-assistant.html"',
    'href="pages/qs-takeoff.html"',
    "professional delivery",
    "2024 - present",
    "msc design + ai",
    "download portfolio brief",
    "two-page portfolio brief",
]
CASE_STUDY_REQUIREMENTS = {
    "pages/aec-rag.html": [
        "aec-rag-system-map.svg",
        "document hit@1",
        "exact-target hit@1",
        "retained failure",
        "document assistance only",
        "evaluate_retrieval.py",
        "test_rag.py",
        "open source",
        "read evaluation",
    ],
    "pages/embodied-ai.html": [
        "embodied-system-map.svg",
        "filtered success",
        "shifted rgb success",
        "retained failure",
        "no physical camera",
        "evaluate_vla.py",
        "test_vla_embodied_agent.py",
        "open source",
        "read evaluation",
    ],
    "pages/massing-explorer.html": [
        "massing-system-map.svg",
        "massing-option-comparison.svg",
        "feasible rate",
        "retained limitation",
        "no code inference",
        "evaluate_massing.py",
        "test_massing_explorer.py",
        "open source",
        "read evaluation",
    ],
    "pages/specification-assistant.html": [
        "specification-system-map.svg",
        "specification-language-stress.svg",
        "requirement f1",
        "exact-case accuracy",
        "retained failure",
        "no open-domain chat",
        "evaluate_specification.py",
        "test_project_specification_copilot.py",
        "open source",
        "read evaluation",
    ],
    "pages/qs-takeoff.html": [
        "qs-system-map.svg",
        "qs-cost-breakdown.svg",
        "qs-tender-comparison.svg",
        "quantity exact match",
        "naive baseline mae",
        "retained limitation",
        "no pdf, cad, bim, or ifc ingestion",
        "evaluate_qs.py",
        "test_qs_takeoff_tender_analysis.py",
        "open source",
        "read evaluation",
    ],
}
CASE_STUDY_COMMON_REQUIREMENTS = [
    'rel="canonical"',
    'property="og:title"',
    'property="og:description"',
    'property="og:url"',
    'property="og:image"',
    'name="twitter:card"',
]
REQUIRED_CSS_INTERACTION_CONTRACTS = [
    ":focus-visible",
    ".skip-link",
    ".skip-link:focus",
    "color: var(--clay)",
    "@media (prefers-reduced-motion: reduce)",
    "scroll-behavior: auto !important",
    "transition-duration: 0.01ms !important",
]
REQUIRED_SCRIPT_INTERACTION_CONTRACTS = [
    "function closeNavigation(restoreFocus)",
    'event.key === "Escape"',
    "closeNavigation(true)",
    "toggle.focus()",
    'window.addEventListener("resize"',
]
COMMAND_COPY_REQUIREMENTS = {
    "index.html": 2,
    "pages/aec-rag.html": 4,
    "pages/embodied-ai.html": 3,
    "pages/massing-explorer.html": 3,
    "pages/qs-takeoff.html": 3,
    "pages/specification-assistant.html": 3,
}
REQUIRED_COMMAND_COPY_SCRIPT_CONTRACTS = [
    'document.querySelectorAll("code[data-copy-command]")',
    'button.setAttribute("data-copy-button", "")',
    "navigator.clipboard.writeText(text)",
    'document.execCommand("copy")',
    'status.setAttribute("aria-live", "polite")',
    'status.setAttribute("aria-atomic", "true")',
    "Command copied to clipboard.",
    "Copy failed. Select the command text manually.",
]
REQUIRED_COMMAND_COPY_CSS_CONTRACTS = [
    ".command-copy",
    ".command-copy code",
    ".copy-command",
    '.copy-command[data-state="success"]',
    '.copy-command[data-state="error"]',
    ".copy-status",
]
CASE_STUDY_ASSET_MIRRORS = {
    "assets/aec-rag-system-map.svg": (
        "projects/aec-code-compliance-rag/demo_outputs/system_map.svg"
    ),
    "assets/embodied-system-map.svg": (
        "projects/vla-embodied-agent-simulator/demo_outputs/system_map.svg"
    ),
    "assets/massing-system-map.svg": (
        "projects/constraint-aware-massing-explorer/demo_outputs/system_map.svg"
    ),
    "assets/massing-option-comparison.svg": (
        "projects/constraint-aware-massing-explorer/demo_outputs/option_comparison.svg"
    ),
    "assets/specification-system-map.svg": (
        "projects/project-specification-copilot/demo_outputs/system_map.svg"
    ),
    "assets/specification-language-stress.svg": (
        "projects/project-specification-copilot/demo_outputs/language_stress_comparison.svg"
    ),
    "assets/qs-system-map.svg": ("projects/qs-takeoff-tender-analysis/demo_outputs/system_map.svg"),
    "assets/qs-cost-breakdown.svg": (
        "projects/qs-takeoff-tender-analysis/demo_outputs/cost_breakdown.svg"
    ),
    "assets/qs-tender-comparison.svg": (
        "projects/qs-takeoff-tender-analysis/demo_outputs/tender_comparison.svg"
    ),
}


class SiteLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self.ids: set[str] = set()
        self.id_counts: dict[str, int] = {}
        self.images: list[dict[str, str | None]] = []
        self.h1_count = 0
        self.title_count = 0
        self.html_lang: str | None = None
        self.meta_description: str | None = None
        self.meta_viewport: str | None = None
        self.meta_theme_color: str | None = None
        self.meta_robots: str | None = None
        self.open_graph: dict[str, str | None] = {}
        self.twitter: dict[str, str | None] = {}
        self.canonical_links: list[str | None] = []
        self.image_preloads: list[dict[str, str | None]] = []
        self.nav_toggles: list[dict[str, str | None]] = []
        self.skip_links: list[str | None] = []
        self.main_content_tabindexes: list[str | None] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "html":
            self.html_lang = attributes.get("lang")
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "title":
            self.title_count += 1
        elif tag == "img":
            self.images.append(attributes)
        elif tag == "meta":
            if attributes.get("name") == "description":
                self.meta_description = attributes.get("content")
            elif attributes.get("name") == "viewport":
                self.meta_viewport = attributes.get("content")
            elif attributes.get("name") == "theme-color":
                self.meta_theme_color = attributes.get("content")
            elif attributes.get("name") == "robots":
                self.meta_robots = attributes.get("content")
            meta_name = attributes.get("name") or ""
            if meta_name.startswith("twitter:"):
                self.twitter[meta_name] = attributes.get("content")
            if attributes.get("property", "").startswith("og:"):
                self.open_graph[attributes["property"]] = attributes.get("content")
        elif tag == "link":
            rels = set((attributes.get("rel") or "").split())
            if "canonical" in rels:
                self.canonical_links.append(attributes.get("href"))
            if "preload" in rels and attributes.get("as") == "image":
                self.image_preloads.append(attributes)

        classes = set((attributes.get("class") or "").split())
        if tag == "a" and "skip-link" in classes:
            self.skip_links.append(attributes.get("href"))
        if tag == "main" and attributes.get("id") == "main-content":
            self.main_content_tabindexes.append(attributes.get("tabindex"))
        if tag == "button" and "nav-toggle" in classes:
            self.nav_toggles.append(
                {
                    "aria-label": attributes.get("aria-label"),
                    "aria-controls": attributes.get("aria-controls"),
                    "aria-expanded": attributes.get("aria-expanded"),
                }
            )

        element_id = attributes.get("id")
        if element_id:
            self.ids.add(element_id)
            self.id_counts[element_id] = self.id_counts.get(element_id, 0) + 1
        for attribute in ("href", "src"):
            value = attributes.get(attribute)
            if value:
                self.links.append((attribute, value))


def html_files() -> list[Path]:
    return sorted(SITE_ROOT.rglob("*.html"))


def public_url(path: Path) -> str:
    relative = path.relative_to(SITE_ROOT).as_posix()
    return PUBLIC_BASE_URL if relative == "index.html" else f"{PUBLIC_BASE_URL}{relative}"


def indexable_html_files() -> list[Path]:
    indexable: list[Path] = []
    for path in html_files():
        parser = SiteLinkParser()
        parser.feed(path.read_text(encoding="utf-8"))
        if parser.meta_robots and "noindex" in parser.meta_robots.lower():
            continue
        indexable.append(path)
    return indexable


def is_external(target: str) -> bool:
    scheme = urlparse(target).scheme
    return scheme in {"data", "http", "https", "mailto", "tel"}


def resolve_local_path(source: Path, target: str) -> tuple[Path, str]:
    parsed = urlparse(target)
    if not parsed.path:
        return source, parsed.fragment
    path = (source.parent / unquote(parsed.path)).resolve()
    return path, parsed.fragment


def check_local_target(source: Path, target: str, ids_by_file: dict[Path, set[str]]) -> str | None:
    path, fragment = resolve_local_path(source, target)
    try:
        path.relative_to(SITE_ROOT.resolve())
    except ValueError:
        return f"{source.relative_to(ROOT)}: local link escapes portfolio-site: {target}"
    if not path.exists():
        return f"{source.relative_to(ROOT)}: missing local target: {target}"
    if fragment and path.suffix == ".html" and fragment not in ids_by_file.get(path, set()):
        return (
            f"{source.relative_to(ROOT)}: missing anchor `{fragment}` in {path.relative_to(ROOT)}"
        )
    return None


def check_placeholders(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8").lower()
    return [
        f"{path.relative_to(ROOT)}: placeholder text remains: {pattern}"
        for pattern in PLACEHOLDER_PATTERNS
        if pattern in text
    ]


def check_html_links() -> list[str]:
    parsed_pages: dict[Path, SiteLinkParser] = {}
    issues: list[str] = []
    for path in html_files():
        parser = SiteLinkParser()
        parser.feed(path.read_text(encoding="utf-8"))
        parsed_pages[path.resolve()] = parser
        issues.extend(check_placeholders(path))

    ids_by_file = {path: parser.ids for path, parser in parsed_pages.items()}
    for path, parser in parsed_pages.items():
        for _attribute, target in parser.links:
            if is_external(target) or target.startswith("#"):
                if target.startswith("#") and target[1:] not in parser.ids:
                    issues.append(f"{path.relative_to(ROOT)}: missing anchor `{target}`")
                continue
            issue = check_local_target(path, target, ids_by_file)
            if issue:
                issues.append(issue)
    return issues


def check_css_assets() -> list[str]:
    issues: list[str] = []
    for path in sorted(SITE_ROOT.rglob("*.css")):
        text = path.read_text(encoding="utf-8")
        issues.extend(check_placeholders(path))
        for match in URL_PATTERN.finditer(text):
            target = match.group("path").strip()
            if (
                not target
                or target.startswith("#")
                or is_external(target)
                or target.startswith("data:")
            ):
                continue
            issue = check_local_target(path, target, {})
            if issue:
                issues.append(issue)
    return issues


def check_page_accessibility_contracts() -> list[str]:
    issues: list[str] = []
    for path in html_files():
        parser = SiteLinkParser()
        parser.feed(path.read_text(encoding="utf-8"))
        label = path.relative_to(ROOT)

        if parser.html_lang != "en":
            issues.append(f"{label}: html language must be `en`")
        if parser.title_count != 1:
            issues.append(f"{label}: expected exactly one title element")
        if parser.h1_count != 1:
            issues.append(f"{label}: expected exactly one h1 element")
        if not parser.meta_viewport:
            issues.append(f"{label}: viewport metadata is missing")
        if not parser.meta_description or len(parser.meta_description.strip()) < 40:
            issues.append(f"{label}: meaningful page description metadata is missing")
        if parser.skip_links != ["#main-content"]:
            issues.append(f"{label}: expected one skip link targeting `#main-content`")
        if parser.main_content_tabindexes != ["-1"]:
            issues.append(f"{label}: expected one focusable main landmark with id `main-content`")

        for index, image in enumerate(parser.images, start=1):
            alt = image.get("alt")
            if alt is None or not alt.strip():
                issues.append(f"{label}: image {index} needs meaningful alternative text")
            width = image.get("width") or ""
            height = image.get("height") or ""
            if not width.isdigit() or int(width) <= 0:
                issues.append(f"{label}: image {index} needs a positive intrinsic width")
            if not height.isdigit() or int(height) <= 0:
                issues.append(f"{label}: image {index} needs a positive intrinsic height")
            if image.get("loading") != "lazy":
                issues.append(f"{label}: image {index} must use lazy loading")
            if image.get("decoding") != "async":
                issues.append(f"{label}: image {index} must use asynchronous decoding")

        duplicate_ids = sorted(
            element_id for element_id, count in parser.id_counts.items() if count > 1
        )
        for element_id in duplicate_ids:
            issues.append(f"{label}: duplicate id `{element_id}`")

        if len(parser.nav_toggles) != 1:
            issues.append(f"{label}: expected exactly one mobile navigation toggle")
            continue
        toggle = parser.nav_toggles[0]
        controlled_id = toggle["aria-controls"]
        if not toggle["aria-label"]:
            issues.append(f"{label}: navigation toggle needs an accessible label")
        if not controlled_id or controlled_id not in parser.ids:
            issues.append(f"{label}: navigation toggle aria-controls target is missing")
        if toggle["aria-expanded"] != "false":
            issues.append(f"{label}: navigation toggle must initialize collapsed")
    return issues


def check_public_discovery_contracts() -> list[str]:
    issues: list[str] = []
    required_open_graph = {"og:type", "og:title", "og:description", "og:url", "og:image"}

    for path in indexable_html_files():
        parser = SiteLinkParser()
        text = path.read_text(encoding="utf-8")
        parser.feed(text)
        label = path.relative_to(ROOT)
        expected_url = public_url(path)

        if parser.canonical_links != [expected_url]:
            issues.append(f"{label}: canonical URL must match `{expected_url}`")
        if not parser.meta_theme_color:
            issues.append(f"{label}: theme-color metadata is missing")
        missing_open_graph = sorted(required_open_graph - parser.open_graph.keys())
        for property_name in missing_open_graph:
            issues.append(f"{label}: social metadata missing: {property_name}")
        if parser.open_graph.get("og:url") != expected_url:
            issues.append(f"{label}: og:url must match the canonical URL")
        if parser.twitter.get("twitter:card") != "summary_large_image":
            issues.append(f"{label}: twitter card must use `summary_large_image`")

    home = SITE_ROOT / "index.html"
    home_text = home.read_text(encoding="utf-8")
    home_parser = SiteLinkParser()
    home_parser.feed(home_text)
    json_ld_matches = list(JSON_LD_PATTERN.finditer(home_text))
    if len(json_ld_matches) != 1:
        issues.append("portfolio-site/index.html: expected exactly one JSON-LD profile block")
    else:
        try:
            profile = json.loads(json_ld_matches[0].group("payload"))
        except json.JSONDecodeError as error:
            issues.append(f"portfolio-site/index.html: invalid JSON-LD: {error}")
        else:
            if profile.get("@type") != "ProfilePage":
                issues.append("portfolio-site/index.html: JSON-LD must describe a ProfilePage")
            if profile.get("mainEntity", {}).get("@type") != "Person":
                issues.append("portfolio-site/index.html: JSON-LD mainEntity must be a Person")
            projects = profile.get("hasPart", [])
            if len(projects) != len(CASE_STUDY_REQUIREMENTS):
                issues.append("portfolio-site/index.html: JSON-LD must list five selected projects")
            expected_project_urls = {
                f"{PUBLIC_BASE_URL}{relative_path}" for relative_path in CASE_STUDY_REQUIREMENTS
            }
            project_urls = {str(project.get("url", "")) for project in projects}
            if project_urls != expected_project_urls:
                issues.append(
                    "portfolio-site/index.html: JSON-LD project URLs must match the five case studies"
                )
            for project in projects:
                if project.get("@type") != "SoftwareSourceCode":
                    issues.append(
                        "portfolio-site/index.html: each JSON-LD project must be SoftwareSourceCode"
                    )
                if not str(project.get("codeRepository", "")).startswith(
                    "https://github.com/josiahsutd-stack/ai-portfolio/"
                ):
                    issues.append(
                        "portfolio-site/index.html: JSON-LD project repository is invalid"
                    )

    not_found = SiteLinkParser()
    not_found.feed((SITE_ROOT / "404.html").read_text(encoding="utf-8"))
    if not_found.meta_robots != "noindex, follow":
        issues.append("portfolio-site/404.html: expected `noindex, follow` robots metadata")
    for _attribute, target in not_found.links:
        if not target.startswith("#") and not target.startswith(PUBLIC_BASE_URL):
            issues.append(
                "portfolio-site/404.html: assets and routes must remain valid from nested missing URLs"
            )

    sitemap_path = SITE_ROOT / "sitemap.xml"
    try:
        sitemap = ET.parse(sitemap_path)
    except (ET.ParseError, OSError) as error:
        issues.append(f"portfolio-site/sitemap.xml: invalid sitemap: {error}")
    else:
        namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        sitemap_urls = {element.text for element in sitemap.findall("s:url/s:loc", namespace)}
        expected_urls = {public_url(path) for path in indexable_html_files()}
        if sitemap_urls != expected_urls:
            issues.append("portfolio-site/sitemap.xml: URLs must match all indexable HTML pages")

    robots_path = SITE_ROOT / "robots.txt"
    robots = robots_path.read_text(encoding="utf-8") if robots_path.exists() else ""
    if "User-agent: *" not in robots or "Allow: /" not in robots:
        issues.append("portfolio-site/robots.txt: public crawl policy is missing")
    if f"Sitemap: {PUBLIC_BASE_URL}sitemap.xml" not in robots:
        issues.append("portfolio-site/robots.txt: sitemap route is missing")

    return issues


def png_dimensions(path: Path) -> tuple[int, int] | None:
    header = path.read_bytes()[:24]
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", header[16:24])


def check_social_preview_contracts() -> list[str]:
    issues: list[str] = []
    required_open_graph = {
        "og:type",
        "og:site_name",
        "og:locale",
        "og:title",
        "og:description",
        "og:url",
        "og:image",
        "og:image:secure_url",
        "og:image:type",
        "og:image:width",
        "og:image:height",
        "og:image:alt",
    }
    required_twitter = {
        "twitter:card",
        "twitter:title",
        "twitter:description",
        "twitter:image",
        "twitter:image:alt",
    }
    indexable_paths = {path.relative_to(SITE_ROOT).as_posix() for path in indexable_html_files()}
    configured_paths = set(SOCIAL_CARD_REQUIREMENTS)
    if configured_paths != indexable_paths:
        missing = sorted(indexable_paths - configured_paths)
        stale = sorted(configured_paths - indexable_paths)
        if missing:
            issues.append(f"social preview manifest is missing pages: {', '.join(missing)}")
        if stale:
            issues.append(f"social preview manifest has stale pages: {', '.join(stale)}")

    for relative_page, (relative_card, expected_alt) in SOCIAL_CARD_REQUIREMENTS.items():
        page_path = SITE_ROOT / relative_page
        label = page_path.relative_to(ROOT)
        if not page_path.is_file():
            issues.append(f"{label}: social preview page is missing")
            continue

        parser = SiteLinkParser()
        parser.feed(page_path.read_text(encoding="utf-8"))
        for property_name in sorted(required_open_graph - parser.open_graph.keys()):
            issues.append(f"{label}: social metadata missing: {property_name}")
        for meta_name in sorted(required_twitter - parser.twitter.keys()):
            issues.append(f"{label}: social metadata missing: {meta_name}")

        expected_image = f"{PUBLIC_BASE_URL}{relative_card}"
        expected_open_graph = {
            "og:site_name": SOCIAL_SITE_NAME,
            "og:locale": SOCIAL_LOCALE,
            "og:url": public_url(page_path),
            "og:image": expected_image,
            "og:image:secure_url": expected_image,
            "og:image:type": "image/png",
            "og:image:width": "1200",
            "og:image:height": "630",
            "og:image:alt": expected_alt,
        }
        for property_name, expected_value in expected_open_graph.items():
            if parser.open_graph.get(property_name) != expected_value:
                issues.append(f"{label}: {property_name} must equal `{expected_value}`")

        expected_twitter = {
            "twitter:card": "summary_large_image",
            "twitter:title": parser.open_graph.get("og:title"),
            "twitter:description": parser.open_graph.get("og:description"),
            "twitter:image": expected_image,
            "twitter:image:alt": expected_alt,
        }
        for meta_name, expected_value in expected_twitter.items():
            if parser.twitter.get(meta_name) != expected_value:
                issues.append(f"{label}: {meta_name} must equal `{expected_value}`")

        card_path = SITE_ROOT / relative_card
        if not card_path.is_file():
            issues.append(f"portfolio-site/{relative_card}: social preview image is missing")
        elif png_dimensions(card_path) != (1200, 630):
            issues.append(f"portfolio-site/{relative_card}: social preview must be a 1200x630 PNG")
    return issues


def check_hero_preload_contracts() -> list[str]:
    issues: list[str] = []
    for relative_path, (href, content_type) in HERO_PRELOAD_REQUIREMENTS.items():
        path = SITE_ROOT / relative_path
        parser = SiteLinkParser()
        parser.feed(path.read_text(encoding="utf-8"))
        expected = {
            "href": href,
            "type": content_type,
            "fetchpriority": "high",
        }
        if len(parser.image_preloads) != 1 or any(
            parser.image_preloads[0].get(key) != value for key, value in expected.items()
        ):
            issues.append(
                f"portfolio-site/{relative_path}: expected one matching high-priority hero preload"
            )
    return issues


def check_shared_interaction_contracts() -> list[str]:
    issues: list[str] = []
    css = (SITE_ROOT / "styles.css").read_text(encoding="utf-8")
    script = (SITE_ROOT / "site.js").read_text(encoding="utf-8")

    issues.extend(
        f"portfolio-site/styles.css: interaction contract missing: {requirement}"
        for requirement in REQUIRED_CSS_INTERACTION_CONTRACTS
        if requirement not in css
    )
    issues.extend(
        f"portfolio-site/site.js: interaction contract missing: {requirement}"
        for requirement in REQUIRED_SCRIPT_INTERACTION_CONTRACTS
        if requirement not in script
    )
    return issues


def check_command_copy_contracts() -> list[str]:
    issues: list[str] = []
    for relative_path, expected_count in COMMAND_COPY_REQUIREMENTS.items():
        path = SITE_ROOT / relative_path
        text = path.read_text(encoding="utf-8")
        marked_count = len(re.findall(r"<code\s+data-copy-command(?:\s|>)", text))
        code_count = len(re.findall(r"<code(?:\s|>)", text))
        label = path.relative_to(ROOT)
        if marked_count != expected_count:
            issues.append(
                f"{label}: expected {expected_count} copyable commands, found {marked_count}"
            )
        if code_count != marked_count:
            issues.append(f"{label}: every visible command block must opt into one-click copying")

    script = (SITE_ROOT / "site.js").read_text(encoding="utf-8")
    css = (SITE_ROOT / "styles.css").read_text(encoding="utf-8")
    issues.extend(
        f"portfolio-site/site.js: command-copy contract missing: {requirement}"
        for requirement in REQUIRED_COMMAND_COPY_SCRIPT_CONTRACTS
        if requirement not in script
    )
    issues.extend(
        f"portfolio-site/styles.css: command-copy contract missing: {requirement}"
        for requirement in REQUIRED_COMMAND_COPY_CSS_CONTRACTS
        if requirement not in css
    )
    return issues


def relative_luminance(hex_color: str) -> float:
    channels = [int(hex_color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(foreground: str, background: str) -> float:
    light, dark = sorted(
        [relative_luminance(foreground), relative_luminance(background)],
        reverse=True,
    )
    return (light + 0.05) / (dark + 0.05)


def check_palette_contrast() -> list[str]:
    css = (SITE_ROOT / "styles.css").read_text(encoding="utf-8")
    palette = {
        match.group("name"): match.group("value") for match in CSS_VARIABLE_PATTERN.finditer(css)
    }
    issues: list[str] = []
    for foreground, background, minimum in REQUIRED_CONTRAST_PAIRS:
        if foreground not in palette or background not in palette:
            issues.append(
                "portfolio-site/styles.css: required contrast color variable missing: "
                f"{foreground} or {background}"
            )
            continue
        ratio = contrast_ratio(palette[foreground], palette[background])
        if ratio < minimum:
            issues.append(
                "portfolio-site/styles.css: contrast failure for "
                f"{foreground} on {background}: {ratio:.2f}:1 < {minimum:.1f}:1"
            )
    return issues


def check_home_evidence_labels() -> list[str]:
    index = SITE_ROOT / "index.html"
    text = index.read_text(encoding="utf-8").lower()
    issues = [
        f"portfolio-site/index.html: required visual missing: {asset}"
        for asset in REQUIRED_HOME_ASSETS
        if asset.lower() not in text
        and asset.lower() not in (SITE_ROOT / "styles.css").read_text(encoding="utf-8").lower()
    ]
    issues.extend(
        f"portfolio-site/index.html: visual boundary missing: {boundary}"
        for boundary in REQUIRED_HOME_BOUNDARIES
        if boundary not in text
    )
    issues.extend(
        f"portfolio-site/index.html: required section text missing: {section}"
        for section in REQUIRED_HOME_SECTIONS
        if section not in text
    )
    return issues


def check_case_studies() -> list[str]:
    issues: list[str] = []
    for relative_path, requirements in CASE_STUDY_REQUIREMENTS.items():
        path = SITE_ROOT / relative_path
        if not path.exists():
            issues.append(f"portfolio-site/{relative_path}: required case study is missing")
            continue
        text = path.read_text(encoding="utf-8").lower()
        issues.extend(
            f"portfolio-site/{relative_path}: required case-study evidence missing: {requirement}"
            for requirement in [*CASE_STUDY_COMMON_REQUIREMENTS, *requirements]
            if requirement not in text
        )
    return issues


def check_case_study_asset_mirrors() -> list[str]:
    issues: list[str] = []
    for site_asset, source_artifact in CASE_STUDY_ASSET_MIRRORS.items():
        site_path = SITE_ROOT / site_asset
        source_path = ROOT / source_artifact
        if not site_path.exists() or not source_path.exists():
            issues.append(
                f"portfolio-site/{site_asset}: mirrored evidence asset or source is missing"
            )
            continue
        if site_path.read_bytes() != source_path.read_bytes():
            issues.append(
                f"portfolio-site/{site_asset}: mirrored evidence asset is stale; "
                f"copy {source_artifact}"
            )
    return issues


def main() -> None:
    if not SITE_ROOT.exists():
        raise SystemExit("portfolio-site directory is missing")
    issues = (
        check_html_links()
        + check_css_assets()
        + check_page_accessibility_contracts()
        + check_public_discovery_contracts()
        + check_social_preview_contracts()
        + check_hero_preload_contracts()
        + check_shared_interaction_contracts()
        + check_command_copy_contracts()
        + check_palette_contrast()
        + check_home_evidence_labels()
        + check_case_studies()
        + check_case_study_asset_mirrors()
    )
    if issues:
        print("Portfolio site check failed:")
        for issue in issues:
            print(f"- {issue}")
        sys.exit(1)
    print(f"Portfolio site check passed for {len(html_files())} HTML pages.")


if __name__ == "__main__":
    main()
