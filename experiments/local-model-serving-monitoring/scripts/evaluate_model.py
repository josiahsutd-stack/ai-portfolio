from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

from local_model_serving_monitoring import (  # noqa: E402
    detect_drift,
    generate_churn_data,
    generate_monitoring_report,
    list_prediction_logs,
    log_prediction,
    predict_churn,
    save_model_artifact,
    train_churn_model,
)


def _repo_relative_artifacts(artifacts: dict[str, str]) -> dict[str, str]:
    return {
        key: Path(value).resolve().relative_to(REPO_ROOT).as_posix()
        for key, value in artifacts.items()
    }


def _stable_prediction_logs(logs: list[dict[str, object]]) -> list[dict[str, object]]:
    stable = [dict(log) for log in logs]
    for log in stable:
        log["created_at"] = "generated-at-runtime"
    return stable


def _write_report(summary: dict[str, object], output_path: Path) -> None:
    metrics = summary["metrics"]
    drift = summary["drift"]
    lines = [
        "# Local Model Evaluation Report",
        "",
        "Synthetic local evaluation for the Local Model Serving and Monitoring Scaffold.",
        "",
        "## Model Metrics",
        "",
    ]
    for key in ["accuracy", "precision", "recall", "f1", "roc_auc", "brier_score"]:
        lines.append(f"- {key}: {metrics[key]}")
    lines.extend(
        [
            "",
            "## Artifact Metadata",
            "",
            f"- model_version: {metrics['version']}",
            f"- schema_version: {metrics['schema_version']}",
            f"- train_rows: {metrics['train_rows']}",
            f"- test_rows: {metrics['test_rows']}",
            "",
            "## Drift Simulation",
            "",
            f"- drift_detected: {drift['drift_detected']}",
            f"- top_drifted_features: {', '.join(drift['top_drifted_features']) or 'None'}",
            "",
            "## Boundaries",
            "",
            "- Synthetic churn data only.",
            "- Local joblib and JSON artifact files only.",
            "- Not production monitoring and not a real customer-retention decision system.",
        ]
    )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    output_dir = PROJECT_ROOT / "demo_outputs"
    output_dir.mkdir(exist_ok=True)

    reference = generate_churn_data(rows=180)
    shifted = reference.assign(usage_score=reference["usage_score"] * 0.2)
    model, metrics = train_churn_model(reference)
    artifacts = save_model_artifact(model, metrics, artifact_dir=output_dir / "model_artifacts")
    sample_payload = {
        "tenure_months": 12,
        "monthly_spend": 80,
        "support_tickets": 3,
        "usage_score": 0.6,
    }
    prediction = predict_churn(model, sample_payload)
    drift = detect_drift(reference, shifted, threshold=0.1)

    db_path = output_dir / "eval_predictions.sqlite"
    if db_path.exists():
        db_path.unlink()
    log_prediction(
        sample_payload,
        prediction,
        model_version=str(metrics["version"]),
        db_path=db_path,
        request_id="demo-request-1",
        latency_ms=12,
    )
    logs = list_prediction_logs(db_path=db_path)

    monitoring_report = generate_monitoring_report(reference, shifted, prediction_logs=logs)
    summary = {
        "dataset": "synthetic generated churn data",
        "metrics": metrics,
        "artifacts": _repo_relative_artifacts(artifacts),
        "sample_prediction": prediction,
        "drift": drift,
        "monitoring_report": monitoring_report,
    }
    (output_dir / "model_eval_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "sample_prediction_log.json").write_text(
        json.dumps(_stable_prediction_logs(logs), indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "drift_report.md").write_text(
        "# Drift Report\n\n"
        "Synthetic drift simulation for local review.\n\n"
        f"- Drift detected: {drift['drift_detected']}\n"
        f"- Top drifted features: {', '.join(drift['top_drifted_features']) or 'None'}\n"
        f"- Scores: `{json.dumps(drift['scores'], sort_keys=True)}`\n",
        encoding="utf-8",
    )
    _write_report(summary, output_dir / "model_eval_report.md")
    print(json.dumps({"metrics": metrics, "drift_detected": drift["drift_detected"]}, indent=2))
    print(f"Wrote local model demo outputs to {output_dir}")


if __name__ == "__main__":
    main()
