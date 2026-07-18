from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
SITE_ROOT = ROOT / "portfolio-site"
PLACEHOLDER_PATTERNS = [
    "your-username",
    "your-name",
    "your.email",
    "example.com",
]
URL_PATTERN = re.compile(r"url\((?P<quote>['\"]?)(?P<path>.*?)(?P=quote)\)")
CSS_VARIABLE_PATTERN = re.compile(r"--(?P<name>[a-z0-9-]+):\s*(?P<value>#[0-9a-fA-F]{6})")
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
        self.image_alts: list[str | None] = []
        self.h1_count = 0
        self.title_count = 0
        self.html_lang: str | None = None
        self.meta_description: str | None = None
        self.meta_viewport: str | None = None
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
            self.image_alts.append(attributes.get("alt"))
        elif tag == "meta":
            if attributes.get("name") == "description":
                self.meta_description = attributes.get("content")
            elif attributes.get("name") == "viewport":
                self.meta_viewport = attributes.get("content")

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

        for index, alt in enumerate(parser.image_alts, start=1):
            if alt is None or not alt.strip():
                issues.append(f"{label}: image {index} needs meaningful alternative text")

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
        + check_shared_interaction_contracts()
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
