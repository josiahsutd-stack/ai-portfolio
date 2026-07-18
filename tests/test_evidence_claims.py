import json
from pathlib import Path

import yaml

from scripts.check_evidence_claims import (
    check_ledger,
    check_public_assertions,
    format_metric,
    materialize_claims,
    render_ledger,
    resolve_json_path,
)


def write_fixture_repo(root: Path, public_text: str = "Accuracy 0.750") -> dict[str, object]:
    (root / "projects" / "demo").mkdir(parents=True)
    (root / "docs").mkdir()
    (root / "projects" / "projects.yml").write_text(
        yaml.safe_dump(
            {
                "projects": [
                    {
                        "slug": "demo",
                        "name": "Demo Classifier",
                        "readme_path": "projects/demo/README.md",
                        "boundary": "Synthetic fixture only",
                    }
                ]
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    (root / "projects" / "demo" / "metrics.json").write_text(
        json.dumps({"summary": {"accuracy": 0.75}}), encoding="utf-8"
    )
    (root / "README.md").write_text(public_text, encoding="utf-8")
    return {
        "claims": [
            {
                "id": "demo-accuracy",
                "project_slug": "demo",
                "artifact": "projects/demo/metrics.json",
                "command": "python evaluate.py",
                "evaluation_scope": "Synthetic fixture",
                "metrics": {"accuracy": {"json_path": "summary.accuracy", "decimals": 3}},
                "result_template": "Accuracy {accuracy}",
                "public_surfaces": [{"path": "README.md", "contains": ["Accuracy {accuracy}"]}],
            }
        ]
    }


def test_metric_resolution_and_precision() -> None:
    payload = {"summary": {"score": 0.5, "count": 12}}

    assert resolve_json_path(payload, "summary.score") == 0.5
    assert format_metric(payload["summary"]["score"], {"decimals": 3}) == "0.500"
    assert format_metric(payload["summary"]["count"], {}) == "12"


def test_public_assertion_detects_stale_displayed_metric(tmp_path: Path) -> None:
    config = write_fixture_repo(tmp_path, public_text="Accuracy 0.700")
    contexts, issues = materialize_claims(config, tmp_path)

    assert not issues
    assertion_issues = check_public_assertions(contexts, tmp_path)
    assert len(assertion_issues) == 1
    assert "Accuracy 0.750" in assertion_issues[0]


def test_missing_artifact_fails_materialization(tmp_path: Path) -> None:
    config = write_fixture_repo(tmp_path)
    (tmp_path / "projects" / "demo" / "metrics.json").unlink()

    contexts, issues = materialize_claims(config, tmp_path)

    assert not contexts
    assert issues == ["demo-accuracy: missing evidence artifact `projects/demo/metrics.json`"]


def test_generated_ledger_must_match_current_artifact(tmp_path: Path) -> None:
    config = write_fixture_repo(tmp_path)
    contexts, issues = materialize_claims(config, tmp_path)
    assert not issues
    (tmp_path / "docs" / "EVIDENCE_LEDGER.md").write_text(render_ledger(contexts), encoding="utf-8")

    assert check_ledger(contexts, tmp_path) == []
    (tmp_path / "projects" / "demo" / "metrics.json").write_text(
        json.dumps({"summary": {"accuracy": 0.8}}), encoding="utf-8"
    )
    changed_contexts, changed_issues = materialize_claims(config, tmp_path)

    assert not changed_issues
    assert check_ledger(changed_contexts, tmp_path)


def test_ledger_scope_is_rendered_from_artifact_values(tmp_path: Path) -> None:
    config = write_fixture_repo(tmp_path)
    config["claims"][0]["evaluation_scope"] = "Synthetic fixture at {accuracy} accuracy"
    contexts, issues = materialize_claims(config, tmp_path)

    assert not issues
    assert "Synthetic fixture at 0.750 accuracy" in render_ledger(contexts)


def test_ledger_can_distinguish_multiple_evaluations_for_one_project(tmp_path: Path) -> None:
    config = write_fixture_repo(tmp_path)
    config["claims"][0]["ledger_label"] = "Demo Classifier - Stress Audit"
    contexts, issues = materialize_claims(config, tmp_path)

    assert not issues
    ledger = render_ledger(contexts)
    assert "[Demo Classifier - Stress Audit](../projects/demo/README.md)" in ledger


def test_ledger_uses_manifest_readme_path_for_experiments(tmp_path: Path) -> None:
    config = write_fixture_repo(tmp_path)
    manifest_path = tmp_path / "projects" / "projects.yml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest["projects"][0]["readme_path"] = "experiments/demo/README.md"
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

    contexts, issues = materialize_claims(config, tmp_path)

    assert not issues
    assert "[Demo Classifier](../experiments/demo/README.md)" in render_ledger(contexts)


def test_cross_project_subject_can_own_an_evidence_claim(tmp_path: Path) -> None:
    config = write_fixture_repo(tmp_path)
    config["subjects"] = {
        "demo-integration": {
            "name": "Demo Integration Contract",
            "readme_path": "integrations/demo/README.md",
            "boundary": "One synthetic contract fixture",
        }
    }
    config["claims"][0]["project_slug"] = "demo-integration"

    contexts, issues = materialize_claims(config, tmp_path)

    assert not issues
    ledger = render_ledger(contexts)
    assert "[Demo Integration Contract](../integrations/demo/README.md)" in ledger
    assert "One synthetic contract fixture" in ledger
