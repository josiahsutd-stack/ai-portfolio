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
REQUIRED_HOME_ASSETS = [
    "assets/applied-ai-construction-hero.webp",
    "assets/embodied-ai-concept.webp",
    "assets/architecture-ai-transfer-map.webp",
    "assets/bamboo-factory-thesis.webp",
    "assets/tideline-commons-concept.webp",
    "assets/monsoon-works-concept.webp",
]
REQUIRED_HOME_BOUNDARIES = [
    "not a simulator screenshot or hardware evidence",
    "ai-assisted visualization anchored to original drawings",
    "not commissioned or built",
    "not structural design or a fabrication package",
]
REQUIRED_HOME_SECTIONS = [
    "focused experiments",
    "prioritizes implementation evidence over project count",
]


class SiteLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        element_id = attributes.get("id")
        if element_id:
            self.ids.add(element_id)
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


def check_home_evidence_labels() -> list[str]:
    index = SITE_ROOT / "index.html"
    text = index.read_text(encoding="utf-8").lower()
    issues = [
        f"portfolio-site/index.html: required visual missing: {asset}"
        for asset in REQUIRED_HOME_ASSETS
        if asset not in text and asset not in (SITE_ROOT / "styles.css").read_text(encoding="utf-8")
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


def main() -> None:
    if not SITE_ROOT.exists():
        raise SystemExit("portfolio-site directory is missing")
    issues = check_html_links() + check_css_assets() + check_home_evidence_labels()
    if issues:
        print("Portfolio site check failed:")
        for issue in issues:
            print(f"- {issue}")
        sys.exit(1)
    print(f"Portfolio site check passed for {len(html_files())} HTML pages.")


if __name__ == "__main__":
    main()
