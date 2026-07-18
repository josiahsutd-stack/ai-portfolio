from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.generate_system_maps import build_specs  # noqa: E402
from shared.portfolio_visuals import render_system_map  # noqa: E402

SELECTED_PROJECTS = (
    "aec-code-compliance-rag",
    "vla-embodied-agent-simulator",
    "constraint-aware-massing-explorer",
    "project-specification-copilot",
    "qs-takeoff-tender-analysis",
)
RICH_MAP_MARKERS = (
    "EXECUTED SYSTEM JOURNEY",
    "PROOF, CONTROLS, AND FAILURE BOUNDARIES",
    "HUMAN REVIEW BOUNDARY:",
    "GENERATED FROM",
)


def _check_svg(path: Path, expected: str) -> list[str]:
    issues: list[str] = []
    relative = path.relative_to(ROOT).as_posix()
    if not path.exists():
        return [f"{relative}: missing generated system map"]

    current = path.read_text(encoding="utf-8")
    if current != expected:
        issues.append(f"{relative}: stale; run python scripts/generate_system_maps.py")
    for marker in RICH_MAP_MARKERS:
        if marker not in current:
            issues.append(f"{relative}: missing visual contract marker {marker!r}")

    try:
        root = ET.fromstring(current)
    except ET.ParseError as exc:
        return [*issues, f"{relative}: invalid SVG XML: {exc}"]

    if root.attrib.get("viewBox") != "0 0 1400 840":
        issues.append(f"{relative}: unexpected viewBox")
    if root.attrib.get("role") != "img":
        issues.append(f"{relative}: missing role=img")
    if root.attrib.get("aria-labelledby") != "map-title map-desc":
        issues.append(f"{relative}: missing accessible title/description binding")

    namespace = {"svg": "http://www.w3.org/2000/svg"}
    metadata = root.find("svg:metadata", namespace)
    if metadata is None or not metadata.text:
        issues.append(f"{relative}: missing machine-readable provenance metadata")
    else:
        try:
            payload = json.loads(metadata.text)
        except json.JSONDecodeError as exc:
            issues.append(f"{relative}: invalid provenance metadata: {exc}")
        else:
            if not payload.get("sources"):
                issues.append(f"{relative}: provenance metadata has no sources")
            if len(payload.get("stages", [])) != 5:
                issues.append(f"{relative}: provenance metadata must record five stages")
            if len(payload.get("evidence", [])) != 3:
                issues.append(f"{relative}: provenance metadata must record three evidence panels")
    return issues


def collect_issues() -> list[str]:
    issues: list[str] = []
    specs = build_specs()

    for project in SELECTED_PROJECTS:
        project_root = ROOT / "projects" / project
        readme = project_root / "README.md"
        architecture = project_root / "ARCHITECTURE.md"
        map_relative = f"projects/{project}/demo_outputs/system_map.svg"
        map_path = ROOT / map_relative

        for path in (readme, architecture):
            text = path.read_text(encoding="utf-8")
            relative = path.relative_to(ROOT).as_posix()
            if "```mermaid" in text:
                issues.append(
                    f"{relative}: generic Mermaid block remains on a selected-project page"
                )
            if "demo_outputs/system_map.svg" not in text:
                issues.append(f"{relative}: generated system map is not linked")

        readme_lines = readme.read_text(encoding="utf-8").splitlines()
        map_lines = [
            index
            for index, line in enumerate(readme_lines, start=1)
            if "demo_outputs/system_map.svg" in line
        ]
        if not map_lines or map_lines[0] > 20:
            issues.append(
                f"projects/{project}/README.md: system map must appear within the first 20 lines"
            )

        spec = specs.get(map_relative)
        if spec is None:
            issues.append(f"{map_relative}: no generation specification")
        else:
            issues.extend(_check_svg(map_path, render_system_map(spec)))

    integration_architecture = ROOT / "integrations" / "aec-design-to-cost" / "ARCHITECTURE.md"
    integration_text = integration_architecture.read_text(encoding="utf-8")
    if "```mermaid" in integration_text:
        issues.append(
            "integrations/aec-design-to-cost/ARCHITECTURE.md: generic Mermaid block remains"
        )
    if "demo_outputs/workflow_trace.svg" not in integration_text:
        issues.append(
            "integrations/aec-design-to-cost/ARCHITECTURE.md: executed workflow map is not linked"
        )

    maps_index = (ROOT / "docs" / "architecture-diagrams.md").read_text(encoding="utf-8")
    for project in SELECTED_PROJECTS:
        expected_link = f"../projects/{project}/demo_outputs/system_map.svg"
        if expected_link not in maps_index:
            issues.append(f"docs/architecture-diagrams.md: missing {project} system-map link")
    return issues


def main() -> None:
    issues = collect_issues()
    if issues:
        print("Visual contract check failed:")
        for issue in issues:
            print(f"- {issue}")
        raise SystemExit(1)
    print(
        "Visual contract check passed for 5 generated selected-project maps and the executed integration map."
    )


if __name__ == "__main__":
    main()
