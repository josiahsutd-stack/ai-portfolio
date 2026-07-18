from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

from building_energy_ml_pipeline import (  # noqa: E402
    evaluate_energy_model_detailed,
    load_energy_data,
)


def _write_report(summary: dict[str, object], path: Path) -> None:
    split = summary["split"]
    model_metrics = summary["model"]["metrics"]
    baseline_metrics = summary["baseline"]["metrics"]
    comparison = summary["comparison"]
    example = summary["holdout_example"]
    lines = [
        "# Building Energy Regression Evaluation",
        "",
        "Fixed-split evaluation on the bundled synthetic dataset. These results do not measure real building performance or simulation accuracy.",
        "",
        "## Protocol",
        "",
        f"- Rows: {summary['dataset']['row_count']} synthetic records",
        f"- Split: {split['train_rows']} train / {split['test_rows']} holdout",
        f"- Split seed: {split['random_state']}",
        "- Baseline: predict the training-target mean for every holdout row",
        "",
        "## Results",
        "",
        "| System | MAE (kWh/m2/year) | R2 |",
        "| --- | ---: | ---: |",
        f"| Random forest | {model_metrics['mae']:.2f} | {model_metrics['r2']:.3f} |",
        f"| Training-mean baseline | {baseline_metrics['mae']:.2f} | {baseline_metrics['r2']:.3f} |",
        "",
        f"The random forest reduces MAE by {comparison['mae_reduction_fraction_vs_mean_baseline']:.3f} relative to this baseline on the fixed synthetic holdout.",
        "",
        "## One Holdout Example",
        "",
        f"- Source row index: {example['source_row_index']}",
        f"- Actual synthetic target: {example['actual_kwh_m2_year']:.2f} kWh/m2/year",
        f"- Prediction: {example['predicted_kwh_m2_year']:.2f} kWh/m2/year",
        f"- Absolute error: {example['absolute_error_kwh_m2_year']:.2f} kWh/m2/year",
        "",
        "## Interpretation Boundary",
        "",
        "- The target is generated from hand-authored relationships plus random noise.",
        "- One fixed split is regression evidence, not a robust estimate of real-world generalization.",
        "- No measured utility data, weather files, calibrated simulation, uncertainty intervals, or external validation are included.",
        "- The values must not be used for design, compliance, investment, or engineering decisions.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    data_path = PROJECT_ROOT / "sample_data" / "synthetic_building_energy.csv"
    output_dir = PROJECT_ROOT / "demo_outputs"
    output_dir.mkdir(exist_ok=True)

    summary = evaluate_energy_model_detailed(load_energy_data(data_path))
    summary["dataset"]["path"] = data_path.relative_to(REPO_ROOT).as_posix()
    (output_dir / "energy_eval_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    _write_report(summary, output_dir / "energy_eval_report.md")
    print(json.dumps(summary, indent=2))
    print(f"Wrote building-energy evaluation artifacts to {output_dir}")


if __name__ == "__main__":
    main()
