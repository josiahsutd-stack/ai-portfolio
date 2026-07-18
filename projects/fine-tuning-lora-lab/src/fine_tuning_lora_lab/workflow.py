from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LoRAConfig:
    base_model: str = "small-local-or-remote-model-placeholder"
    rank: int = 8
    alpha: int = 16
    task: str = "support_ticket_classification"


def generate_instruction_dataset() -> list[dict[str, str]]:
    labels = ["billing", "technical", "account", "sales"]
    return [
        {
            "instruction": "Classify this support ticket.",
            "input": f"Customer message about {label} issue number {idx}.",
            "output": label,
        }
        for idx in range(32)
        for label in [labels[idx % len(labels)]]
    ]


def validate_dataset(rows: list[dict[str, str]]) -> dict[str, object]:
    required = {"instruction", "input", "output"}
    invalid = []
    empty_field_rows = []
    duplicate_rows = []
    seen: set[tuple[str, str, str]] = set()
    for idx, row in enumerate(rows):
        if not required.issubset(row):
            invalid.append(idx)
            continue
        if any(not str(row[field]).strip() for field in required):
            empty_field_rows.append(idx)
            invalid.append(idx)
            continue
        signature = tuple(
            str(row[field]).strip().lower() for field in ["instruction", "input", "output"]
        )
        if signature in seen:
            duplicate_rows.append(idx)
            invalid.append(idx)
        seen.add(signature)
    labels = sorted({row.get("output", "") for row in rows if row.get("output")})
    return {
        "valid": not invalid and bool(rows),
        "invalid_rows": invalid,
        "empty_field_rows": empty_field_rows,
        "duplicate_rows": duplicate_rows,
        "labels": labels,
        "row_count": len(rows),
    }


def split_dataset(
    rows: list[dict[str, str]], train_ratio: float = 0.75
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    if not 0 < train_ratio < 1:
        raise ValueError("train_ratio must be between 0 and 1.")
    split = int(len(rows) * train_ratio)
    train, validation = rows[:split], rows[split:]
    if rows and (not train or not validation):
        raise ValueError("Split must produce non-empty train and validation sets.")
    return train, validation


def build_evaluation_template(
    rows: list[dict[str, str]], holdout_size: int = 4
) -> dict[str, object]:
    _train, validation = split_dataset(rows)
    holdout = validation[:holdout_size]
    return {
        "mode": "template_only_no_model_scoring",
        "held_out_prompts": [
            {
                "instruction": row["instruction"],
                "input": row["input"],
                "expected_behavior": f"Classify as `{row['output']}` or explain uncertainty.",
            }
            for row in holdout
        ],
        "checks": [
            "exact label match on held-out prompts",
            "confusion matrix by label",
            "manual review of uncertain cases",
            "overfitting check against duplicate or near-duplicate prompts",
        ],
        "risks": [
            "small synthetic dataset is not evidence of real adaptation",
            "the simulated run does not load or update model parameters",
            "real LoRA training needs GPU/VRAM planning and safety review",
        ],
    }


def simulate_lora_run(
    rows: list[dict[str, str]], config: LoRAConfig | None = None
) -> dict[str, object]:
    validation = validate_dataset(rows)
    if not validation["valid"]:
        raise ValueError("Dataset failed validation.")
    config = config or LoRAConfig()
    train, val = split_dataset(rows)
    return {
        "mode": "simulated_run_no_model_loaded",
        "base_model": config.base_model,
        "rank": config.rank,
        "alpha": config.alpha,
        "task": config.task,
        "train_rows": len(train),
        "validation_rows": len(val),
        "metric_status": "not_computed_no_training",
        "evaluation_template": build_evaluation_template(rows),
    }
