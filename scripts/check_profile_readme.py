from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profile-readme.md"
PROFILE_PREVIEW = ROOT / "portfolio-site" / "assets" / "portfolio-home-preview.jpg"
LEGACY_PROFILE_PREVIEW = ROOT / "portfolio-site" / "assets" / "portfolio-home-preview.png"
GITHUB_REPOSITORY_PREVIEW = ROOT / "portfolio-site" / "assets" / "github-repository-preview.jpg"
GITHUB_REPOSITORY_PREVIEW_MANIFEST = ROOT / "portfolio-site" / "repository-preview-manifest.json"
PORTFOLIO_HOME = ROOT / "portfolio-site" / "index.html"
PORTFOLIO_STYLES = ROOT / "portfolio-site" / "styles.css"
PORTFOLIO_HERO = ROOT / "portfolio-site" / "assets" / "applied-ai-construction-hero.webp"
PROFILE_BRIEF = ROOT / "portfolio-site" / "assets" / "Josiah_Lau_Applied_AI_Portfolio_Brief.pdf"
LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\((?P<target>[^)]+)\)")
REPOSITORY_PREVIEW_SOURCE_PATTERN = re.compile(
    r'<header class="site-header">.*?</header>\s*'
    r'<main id="main-content"[^>]*>\s*'
    r'<section class="hero".*?</section>',
    flags=re.DOTALL,
)
REPOSITORY_PREVIEW_SOURCE_FILES = (
    "portfolio-site/index.html#site-header-and-hero",
    "portfolio-site/styles.css",
    "portfolio-site/assets/applied-ai-construction-hero.webp",
)
REQUIRED_TEXT = (
    "# Josiah Lau | Applied AI Engineer",
    "https://josiahsutd-stack.github.io/ai-portfolio/",
    "https://josiahsutd-stack.github.io/ai-portfolio/assets/Josiah_Lau_Applied_AI_Portfolio_Brief.pdf",
    "https://github.com/josiahsutd-stack/ai-portfolio",
    "https://www.linkedin.com/in/josiah-lau-8041822b6/",
    "mailto:josiahsutd@gmail.com",
    "portfolio-site/assets/portfolio-home-preview.jpg",
    "AEC Code Compliance RAG",
    "Construction Embodied Agent Simulator",
    "Constraint-Aware Massing Explorer",
    "Evidence Policy",
)
FORBIDDEN_PROFILE_PHRASES = (
    "primary review project",
    "recruiter fast path",
    "interview prep",
    "hiring verdict",
    "would hire",
    "would not hire",
    "start with these",
    "projects to inspect",
    "for a 15-minute",
    "the candidate's",
)


def jpeg_dimensions(path: Path) -> tuple[int, int] | None:
    data = path.read_bytes()
    if len(data) < 4 or data[:2] != b"\xff\xd8":
        return None

    start_of_frame_markers = {
        0xC0,
        0xC1,
        0xC2,
        0xC3,
        0xC5,
        0xC6,
        0xC7,
        0xC9,
        0xCA,
        0xCB,
        0xCD,
        0xCE,
        0xCF,
    }
    offset = 2
    while offset + 3 < len(data):
        if data[offset] != 0xFF:
            offset += 1
            continue
        while offset < len(data) and data[offset] == 0xFF:
            offset += 1
        if offset >= len(data):
            return None
        marker = data[offset]
        offset += 1
        if marker in {0x01, *range(0xD0, 0xDA)}:
            continue
        if offset + 2 > len(data):
            return None
        segment_length = int.from_bytes(data[offset : offset + 2], "big")
        if segment_length < 2 or offset + segment_length > len(data):
            return None
        if marker in start_of_frame_markers:
            if segment_length < 7:
                return None
            height = int.from_bytes(data[offset + 3 : offset + 5], "big")
            width = int.from_bytes(data[offset + 5 : offset + 7], "big")
            return width, height
        offset += segment_length
    return None


def repository_preview_source_digest() -> str | None:
    match = REPOSITORY_PREVIEW_SOURCE_PATTERN.search(PORTFOLIO_HOME.read_text(encoding="utf-8"))
    if match is None:
        return None

    digest = hashlib.sha256()
    inputs = (
        (REPOSITORY_PREVIEW_SOURCE_FILES[0], match.group(0).encode("utf-8")),
        (REPOSITORY_PREVIEW_SOURCE_FILES[1], PORTFOLIO_STYLES.read_bytes()),
        (REPOSITORY_PREVIEW_SOURCE_FILES[2], PORTFOLIO_HERO.read_bytes()),
    )
    for label, payload in inputs:
        digest.update(label.encode("utf-8"))
        digest.update(b"\0")
        digest.update(payload)
        digest.update(b"\0")
    return digest.hexdigest()


def repository_preview_manifest_issues() -> list[str]:
    label = "portfolio-site/repository-preview-manifest.json"
    try:
        manifest = json.loads(GITHUB_REPOSITORY_PREVIEW_MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"{label}: invalid manifest: {error}"]

    issues: list[str] = []
    if manifest.get("capture") != {"width": 1280, "height": 640}:
        issues.append(f"{label}: capture must remain 1280x640")
    if tuple(manifest.get("source_files", ())) != REPOSITORY_PREVIEW_SOURCE_FILES:
        issues.append(f"{label}: source file list is stale")

    source_digest = repository_preview_source_digest()
    if source_digest is None:
        issues.append(f"{label}: homepage header and hero source cannot be located")
    elif manifest.get("source_sha256") != source_digest:
        issues.append(
            "portfolio-site/assets/github-repository-preview.jpg: "
            "homepage hero changed after the repository preview was captured"
        )

    if GITHUB_REPOSITORY_PREVIEW.is_file():
        preview_digest = hashlib.sha256(GITHUB_REPOSITORY_PREVIEW.read_bytes()).hexdigest()
        if manifest.get("preview_sha256") != preview_digest:
            issues.append(
                "portfolio-site/assets/github-repository-preview.jpg: preview hash is stale"
            )
    return issues


def collect_issues(text: str | None = None) -> list[str]:
    content = PROFILE.read_text(encoding="utf-8") if text is None else text
    issues: list[str] = []

    for required in REQUIRED_TEXT:
        if required not in content:
            issues.append(f"profile-readme.md: missing required content {required!r}")

    for match in LINK_PATTERN.finditer(content):
        target = match.group("target").strip()
        if not target.startswith(("https://", "mailto:")):
            issues.append(f"profile-readme.md: profile links must be absolute, found {target!r}")

    first_link = LINK_PATTERN.search(content)
    if (
        first_link is None
        or first_link.group("target").strip() != "https://josiahsutd-stack.github.io/ai-portfolio/"
    ):
        issues.append("profile-readme.md: visual portfolio must be the first link")

    lowered = content.lower()
    for phrase in FORBIDDEN_PROFILE_PHRASES:
        if phrase in lowered:
            issues.append(f"profile-readme.md: candidate-facing meta-language {phrase!r}")

    image_line = next(
        (
            index
            for index, line in enumerate(content.splitlines(), start=1)
            if line.startswith("[![")
        ),
        None,
    )
    if image_line is None or image_line > 12:
        issues.append("profile-readme.md: portfolio preview must appear by line 12")

    if not PROFILE_PREVIEW.is_file():
        issues.append("profile-readme.md: local portfolio preview image is missing")
    elif not PROFILE_PREVIEW.read_bytes().startswith(b"\xff\xd8\xff"):
        issues.append("profile-readme.md: portfolio preview must contain JPEG data")

    if LEGACY_PROFILE_PREVIEW.exists():
        issues.append("profile-readme.md: stale PNG-named portfolio preview remains")

    if not GITHUB_REPOSITORY_PREVIEW.is_file():
        issues.append("profile-readme.md: GitHub repository social preview is missing")
    else:
        if jpeg_dimensions(GITHUB_REPOSITORY_PREVIEW) != (1280, 640):
            issues.append(
                "profile-readme.md: GitHub repository social preview must be a 1280x640 JPEG"
            )
        if GITHUB_REPOSITORY_PREVIEW.stat().st_size >= 1_000_000:
            issues.append(
                "profile-readme.md: GitHub repository social preview must remain under 1 MB"
            )
        issues.extend(repository_preview_manifest_issues())

    if not PROFILE_BRIEF.is_file():
        issues.append("profile-readme.md: generated portfolio brief is missing")

    if len(content.splitlines()) > 90:
        issues.append("profile-readme.md: profile entry point exceeds 90 lines")
    return issues


def main() -> None:
    issues = collect_issues()
    if issues:
        print("Profile README check failed:")
        for issue in issues:
            print(f"- {issue}")
        sys.exit(1)
    link_count = len(LINK_PATTERN.findall(PROFILE.read_text(encoding="utf-8")))
    print(f"Profile README check passed with {link_count} absolute links.")


if __name__ == "__main__":
    main()
