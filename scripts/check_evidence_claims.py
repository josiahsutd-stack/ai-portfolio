from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "docs" / "evidence_claims.yml"
LEDGER_PATH = ROOT / "docs" / "EVIDENCE_LEDGER.md"
MANIFEST_PATH = ROOT / "projects" / "projects.yml"


@dataclass(frozen=True)
class ClaimContext:
    claim: dict[str, Any]
    values: dict[str, str]
    project_name: str
    project_readme: str
    boundary: str


def load_yaml_mapping(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected a YAML mapping")
    return payload


def resolve_json_path(payload: Any, json_path: str) -> Any:
    current = payload
    for part in json_path.split("."):
        if not isinstance(current, dict) or part not in current:
            raise KeyError(json_path)
        current = current[part]
    return current


def format_metric(value: Any, specification: dict[str, Any]) -> str:
    if "decimals" in specification:
        decimals = specification["decimals"]
        if not isinstance(decimals, int) or decimals < 0:
            raise ValueError("metric decimals must be a non-negative integer")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("decimal-formatted metric must be numeric")
        return f"{float(value):.{decimals}f}"
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def render_template(template: str, values: dict[str, str]) -> str:
    try:
        return template.format_map(values)
    except KeyError as exc:
        raise ValueError(f"unknown metric placeholder `{exc.args[0]}`") from exc


def _safe_path(root: Path, relative_path: str) -> Path:
    target = (root / relative_path).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"path escapes repository root: {relative_path}") from exc
    return target


def project_index(root: Path) -> dict[str, dict[str, Any]]:
    manifest = load_yaml_mapping(root / MANIFEST_PATH.relative_to(ROOT))
    projects = manifest.get("projects")
    if not isinstance(projects, list):
        raise ValueError("projects/projects.yml: `projects` must be a list")
    return {
        str(project["slug"]): project
        for project in projects
        if isinstance(project, dict) and "slug" in project
    }


def materialize_claims(
    config: dict[str, Any], root: Path = ROOT
) -> tuple[list[ClaimContext], list[str]]:
    claims = config.get("claims")
    if not isinstance(claims, list):
        return [], ["docs/evidence_claims.yml: `claims` must be a list"]
    try:
        projects = project_index(root)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        return [], [str(exc)]

    contexts: list[ClaimContext] = []
    issues: list[str] = []
    seen_ids: set[str] = set()
    for index, claim in enumerate(claims, start=1):
        if not isinstance(claim, dict):
            issues.append(f"claim row {index}: expected a mapping")
            continue
        claim_id = str(claim.get("id", f"row-{index}"))
        if claim_id in seen_ids:
            issues.append(f"{claim_id}: duplicate claim id")
            continue
        seen_ids.add(claim_id)

        slug = str(claim.get("project_slug", ""))
        project = projects.get(slug)
        if project is None:
            issues.append(f"{claim_id}: unknown project slug `{slug}`")
            continue

        artifact_value = claim.get("artifact")
        if not isinstance(artifact_value, str):
            issues.append(f"{claim_id}: artifact must be a repository-relative path")
            continue
        try:
            artifact = _safe_path(root, artifact_value)
        except ValueError as exc:
            issues.append(f"{claim_id}: {exc}")
            continue
        if not artifact.exists():
            issues.append(f"{claim_id}: missing evidence artifact `{artifact_value}`")
            continue
        try:
            payload = json.loads(artifact.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            issues.append(f"{claim_id}: invalid evidence artifact: {exc}")
            continue

        metrics = claim.get("metrics")
        if not isinstance(metrics, dict) or not metrics:
            issues.append(f"{claim_id}: metrics must be a non-empty mapping")
            continue
        values: dict[str, str] = {}
        metric_failed = False
        for metric_name, specification in metrics.items():
            if not isinstance(specification, dict) or not isinstance(
                specification.get("json_path"), str
            ):
                issues.append(f"{claim_id}.{metric_name}: missing json_path")
                metric_failed = True
                continue
            try:
                raw_value = resolve_json_path(payload, specification["json_path"])
                values[str(metric_name)] = format_metric(raw_value, specification)
            except (KeyError, ValueError) as exc:
                issues.append(f"{claim_id}.{metric_name}: {exc}")
                metric_failed = True
        if metric_failed:
            continue
        contexts.append(
            ClaimContext(
                claim=claim,
                values=values,
                project_name=str(project.get("name", slug)),
                project_readme=str(project.get("readme_path", f"projects/{slug}/README.md")),
                boundary=str(project.get("boundary", "")),
            )
        )
    return contexts, issues


def check_public_assertions(contexts: list[ClaimContext], root: Path = ROOT) -> list[str]:
    issues: list[str] = []
    for context in contexts:
        claim_id = str(context.claim["id"])
        surfaces = context.claim.get("public_surfaces")
        if not isinstance(surfaces, list) or not surfaces:
            issues.append(f"{claim_id}: public_surfaces must be a non-empty list")
            continue
        for surface in surfaces:
            if not isinstance(surface, dict) or not isinstance(surface.get("path"), str):
                issues.append(f"{claim_id}: invalid public surface")
                continue
            relative_path = surface["path"]
            try:
                path = _safe_path(root, relative_path)
            except ValueError as exc:
                issues.append(f"{claim_id}: {exc}")
                continue
            if not path.exists():
                issues.append(f"{claim_id}: missing public surface `{relative_path}`")
                continue
            text = path.read_text(encoding="utf-8")
            templates = surface.get("contains")
            if not isinstance(templates, list) or not templates:
                issues.append(f"{claim_id}: `{relative_path}` has no assertions")
                continue
            for template in templates:
                if not isinstance(template, str):
                    issues.append(f"{claim_id}: `{relative_path}` assertion must be text")
                    continue
                try:
                    expected = render_template(template, context.values)
                except ValueError as exc:
                    issues.append(f"{claim_id}: {exc}")
                    continue
                if expected not in text:
                    issues.append(
                        f"{claim_id}: `{relative_path}` is missing artifact-backed text `{expected}`"
                    )
    return issues


def _markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def render_ledger(contexts: list[ClaimContext]) -> str:
    lines = [
        "# Reproducible Evidence Ledger",
        "",
        "This ledger maps selected quantitative results to versioned JSON artifacts and the local commands that produced them. Values and metric-bearing scope text are regenerated and checked for drift by `scripts/check_evidence_claims.py`.",
        "",
        "| Project | Evaluation scope | Current artifact-backed result | Versioned evidence | Reproduce | Interpretation boundary |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for context in contexts:
        claim = context.claim
        result = render_template(str(claim["result_template"]), context.values)
        artifact = str(claim["artifact"])
        artifact_link = f"../{artifact}"
        project_link = f"../{context.project_readme}"
        row = [
            f"[{context.project_name}]({project_link})",
            render_template(str(claim["evaluation_scope"]), context.values),
            result,
            f"[`{Path(artifact).name}`]({artifact_link})",
            f"`{claim['command']}`",
            context.boundary,
        ]
        lines.append("| " + " | ".join(_markdown_cell(value) for value in row) + " |")
    lines.extend(
        [
            "",
            "## Integrity Gate",
            "",
            "The evidence configuration is stored in [`evidence_claims.yml`](evidence_claims.yml). Each metric names an exact JSON path and display precision. The checker fails when an artifact is missing, a JSON path changes, a displayed value becomes stale, or this generated ledger differs from the current artifacts.",
            "",
            "The full local and CI gate is:",
            "",
            "```bash",
            "python scripts/verify.py",
            "```",
            "",
            "These measurements describe only the bundled datasets and simulator scenarios. They are not production, customer, compliance, or physical-safety results.",
            "",
        ]
    )
    return "\n".join(lines)


def check_ledger(contexts: list[ClaimContext], root: Path = ROOT) -> list[str]:
    ledger = root / LEDGER_PATH.relative_to(ROOT)
    if not ledger.exists():
        return ["missing generated evidence ledger: docs/EVIDENCE_LEDGER.md"]
    expected = render_ledger(contexts)
    if ledger.read_text(encoding="utf-8") != expected:
        return [
            "docs/EVIDENCE_LEDGER.md is stale; regenerate with `python scripts/check_evidence_claims.py --write`"
        ]
    return []


def write_ledger(contexts: list[ClaimContext], root: Path = ROOT) -> None:
    ledger = root / LEDGER_PATH.relative_to(ROOT)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text(render_ledger(contexts), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify public metrics against JSON evidence.")
    parser.add_argument("--write", action="store_true", help="Regenerate the evidence ledger.")
    args = parser.parse_args()

    try:
        config = load_yaml_mapping(CONFIG_PATH)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        raise SystemExit(f"Evidence claim check failed:\n- {exc}") from exc
    contexts, issues = materialize_claims(config)
    if args.write and not issues:
        write_ledger(contexts)
    issues.extend(check_public_assertions(contexts))
    issues.extend(check_ledger(contexts))
    if issues:
        print("Evidence claim check failed:")
        for issue in issues:
            print(f"- {issue}")
        sys.exit(1)
    print(
        f"Evidence claim check passed for {len(contexts)} headline claims across "
        f"{sum(len(context.claim['public_surfaces']) for context in contexts)} public surfaces."
    )


if __name__ == "__main__":
    main()
