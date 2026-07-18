from __future__ import annotations

import hashlib
import math
import random
from collections.abc import Iterable
from statistics import mean

DEFAULT_CONFIDENCE_LEVEL = 0.95
DEFAULT_RESAMPLES = 10_000
DEFAULT_SEED = 20_260_718
DEFAULT_WIDE_INTERVAL_THRESHOLD = 0.20


def _rounded(value: float) -> float:
    return round(float(value), 3)


def _validate_confidence_level(confidence_level: float) -> None:
    if confidence_level != DEFAULT_CONFIDENCE_LEVEL:
        raise ValueError("Only the documented 95% interval protocol is supported.")


def _quantile(values: list[float], probability: float) -> float:
    if not values:
        raise ValueError("At least one value is required.")
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower_index = math.floor(position)
    upper_index = math.ceil(position)
    if lower_index == upper_index:
        return ordered[lower_index]
    weight = position - lower_index
    return ordered[lower_index] * (1.0 - weight) + ordered[upper_index] * weight


def _derived_seed(seed: int, label: str) -> int:
    label_digest = hashlib.sha256(label.encode("utf-8")).digest()
    return seed + int.from_bytes(label_digest[:4], byteorder="big")


def _interval_payload(
    *,
    point_estimate: float,
    lower: float,
    upper: float,
    sample_count: int,
    method: str,
    wide_interval_threshold: float,
) -> dict[str, object]:
    width = max(0.0, upper - lower)
    return {
        "point_estimate": _rounded(point_estimate),
        "lower": _rounded(lower),
        "upper": _rounded(upper),
        "width": _rounded(width),
        "sample_count": sample_count,
        "method": method,
        "wide": width > wide_interval_threshold,
    }


def wilson_score_interval(
    values: Iterable[float | bool],
    *,
    confidence_level: float = DEFAULT_CONFIDENCE_LEVEL,
    wide_interval_threshold: float = DEFAULT_WIDE_INTERVAL_THRESHOLD,
) -> dict[str, object]:
    """Return a 95% Wilson score interval for binary case outcomes."""
    _validate_confidence_level(confidence_level)
    observations = [float(value) for value in values]
    if not observations:
        raise ValueError("At least one binary observation is required.")
    if any(value not in {0.0, 1.0} for value in observations):
        raise ValueError("Wilson score intervals require binary observations.")
    sample_count = len(observations)
    point_estimate = mean(observations)
    z = 1.959963984540054
    denominator = 1.0 + (z * z / sample_count)
    center = (point_estimate + z * z / (2.0 * sample_count)) / denominator
    margin = (
        z
        * math.sqrt(
            point_estimate * (1.0 - point_estimate) / sample_count
            + z * z / (4.0 * sample_count * sample_count)
        )
        / denominator
    )
    return _interval_payload(
        point_estimate=point_estimate,
        lower=max(0.0, center - margin),
        upper=min(1.0, center + margin),
        sample_count=sample_count,
        method="wilson_score_95",
        wide_interval_threshold=wide_interval_threshold,
    )


def bootstrap_mean_interval(
    values: Iterable[float],
    *,
    resamples: int = DEFAULT_RESAMPLES,
    seed: int = DEFAULT_SEED,
    confidence_level: float = DEFAULT_CONFIDENCE_LEVEL,
    wide_interval_threshold: float = DEFAULT_WIDE_INTERVAL_THRESHOLD,
) -> dict[str, object]:
    """Return a deterministic percentile interval for a mean over authored cases."""
    _validate_confidence_level(confidence_level)
    observations = [float(value) for value in values]
    if not observations:
        raise ValueError("At least one observation is required.")
    if resamples < 100:
        raise ValueError("At least 100 bootstrap resamples are required.")
    rng = random.Random(seed)
    sample_count = len(observations)
    bootstrap_means = [
        mean(observations[rng.randrange(sample_count)] for _ in range(sample_count))
        for _ in range(resamples)
    ]
    alpha = (1.0 - confidence_level) / 2.0
    return _interval_payload(
        point_estimate=mean(observations),
        lower=_quantile(bootstrap_means, alpha),
        upper=_quantile(bootstrap_means, 1.0 - alpha),
        sample_count=sample_count,
        method=f"percentile_bootstrap_{resamples}_95",
        wide_interval_threshold=wide_interval_threshold,
    )


def paired_bootstrap_mean_interval(
    candidate_values: Iterable[float],
    baseline_values: Iterable[float],
    *,
    resamples: int = DEFAULT_RESAMPLES,
    seed: int = DEFAULT_SEED,
    confidence_level: float = DEFAULT_CONFIDENCE_LEVEL,
    wide_interval_threshold: float = DEFAULT_WIDE_INTERVAL_THRESHOLD,
) -> dict[str, object]:
    """Return a paired percentile interval for candidate-minus-baseline means."""
    _validate_confidence_level(confidence_level)
    candidates = [float(value) for value in candidate_values]
    baselines = [float(value) for value in baseline_values]
    if not candidates or len(candidates) != len(baselines):
        raise ValueError("Candidate and baseline observations must be non-empty and paired.")
    if resamples < 100:
        raise ValueError("At least 100 bootstrap resamples are required.")
    differences = [
        candidate - baseline for candidate, baseline in zip(candidates, baselines, strict=True)
    ]
    sample_count = len(differences)
    rng = random.Random(seed)
    bootstrap_deltas = [
        mean(differences[rng.randrange(sample_count)] for _ in range(sample_count))
        for _ in range(resamples)
    ]
    alpha = (1.0 - confidence_level) / 2.0
    lower = _quantile(bootstrap_deltas, alpha)
    upper = _quantile(bootstrap_deltas, 1.0 - alpha)
    point_estimate = mean(differences)
    payload = _interval_payload(
        point_estimate=point_estimate,
        lower=lower,
        upper=upper,
        sample_count=sample_count,
        method=f"paired_percentile_bootstrap_{resamples}_95",
        wide_interval_threshold=wide_interval_threshold,
    )
    payload.update(
        {
            "candidate_mean": _rounded(mean(candidates)),
            "baseline_mean": _rounded(mean(baselines)),
            "wins": sum(difference > 0.0 for difference in differences),
            "ties": sum(difference == 0.0 for difference in differences),
            "losses": sum(difference < 0.0 for difference in differences),
            "conclusion": (
                "candidate_higher_on_fixed_set"
                if lower > 0.0
                else (
                    "candidate_lower_on_fixed_set"
                    if upper < 0.0
                    else "inconclusive_interval_includes_zero"
                )
            ),
        }
    )
    return payload


def _answerable_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        row
        for row in rows
        if row.get("expected_status") == "answered"
        and row.get("expected_source") != "__NO_ANSWER__"
    ]


def _mode_rows_by_id(mode_payload: dict[str, object]) -> dict[str, dict[str, object]]:
    rows = mode_payload.get("case_metrics")
    if not isinstance(rows, list) or not rows:
        raise ValueError("Mode payload is missing compact case_metrics rows.")
    keyed: dict[str, dict[str, object]] = {}
    for row in rows:
        case_id = str(row.get("case_id", ""))
        if not case_id or case_id in keyed:
            raise ValueError("Mode case_metrics must have unique, non-empty case IDs.")
        if row.get("expected_status") == "answered" and not row.get("expected_no_answer"):
            keyed[case_id] = row
    if not keyed:
        raise ValueError("Mode payload has no answerable case metrics.")
    return keyed


def _paired_mode_comparison(
    *,
    candidate_mode: str,
    baseline_mode: str,
    candidate_payload: dict[str, object],
    baseline_payload: dict[str, object],
    resamples: int,
    seed: int,
    wide_interval_threshold: float,
) -> dict[str, object]:
    candidate_rows = _mode_rows_by_id(candidate_payload)
    baseline_rows = _mode_rows_by_id(baseline_payload)
    if candidate_rows.keys() != baseline_rows.keys():
        missing_from_candidate = sorted(baseline_rows.keys() - candidate_rows.keys())
        missing_from_baseline = sorted(candidate_rows.keys() - baseline_rows.keys())
        raise ValueError(
            "Paired mode comparison requires identical case IDs; "
            f"missing from candidate={missing_from_candidate}, "
            f"missing from baseline={missing_from_baseline}."
        )
    case_ids = sorted(candidate_rows)
    metric_fields = {
        "mean_reciprocal_rank": "reciprocal_rank",
        "retrieval_hit_at_1": "hit_at_1",
        "citation_coverage": "citation_coverage",
    }
    metrics: dict[str, dict[str, object]] = {}
    for metric_name, field_name in metric_fields.items():
        metric_seed = _derived_seed(
            seed,
            f"{candidate_mode}:{baseline_mode}:{metric_name}",
        )
        metrics[metric_name] = paired_bootstrap_mean_interval(
            [float(candidate_rows[case_id][field_name]) for case_id in case_ids],
            [float(baseline_rows[case_id][field_name]) for case_id in case_ids],
            resamples=resamples,
            seed=metric_seed,
            wide_interval_threshold=wide_interval_threshold,
        )
    return {
        "candidate_mode": candidate_mode,
        "baseline_mode": baseline_mode,
        "sample_count": len(case_ids),
        "case_ids": case_ids,
        "metrics": metrics,
    }


def build_retrieval_uncertainty(
    evaluation_payload: dict[str, object],
    ablation_payload: dict[str, object],
    *,
    candidate_mode: str = "hybrid",
    resamples: int = DEFAULT_RESAMPLES,
    seed: int = DEFAULT_SEED,
    wide_interval_threshold: float = DEFAULT_WIDE_INTERVAL_THRESHOLD,
) -> dict[str, object]:
    """Summarize fixed-case uncertainty without implying external validity."""
    rows = evaluation_payload.get("results")
    if not isinstance(rows, list) or not rows:
        raise ValueError("Evaluation payload must include per-case results.")
    answerable = _answerable_rows(rows)
    if not answerable:
        raise ValueError("Evaluation payload has no answerable cases.")
    no_evidence = [row for row in rows if row.get("expected_status") == "no_evidence"]
    review_or_unsupported = [
        row
        for row in rows
        if row.get("expected_status") in {"unsupported_scope", "needs_professional_review"}
    ]

    metrics: dict[str, dict[str, object]] = {
        "retrieval_hit_at_1": wilson_score_interval(
            [
                row.get("expected_source") in list(row.get("retrieved_sources", []))[:1]
                for row in answerable
            ],
            wide_interval_threshold=wide_interval_threshold,
        ),
        "mean_reciprocal_rank": bootstrap_mean_interval(
            [float(row["reciprocal_rank"]) for row in answerable],
            resamples=resamples,
            seed=_derived_seed(seed, "mean_reciprocal_rank"),
            wide_interval_threshold=wide_interval_threshold,
        ),
        "citation_coverage": bootstrap_mean_interval(
            [float(row["citation_coverage"]) for row in answerable],
            resamples=resamples,
            seed=_derived_seed(seed, "citation_coverage"),
            wide_interval_threshold=wide_interval_threshold,
        ),
        "grounding_check_rate": wilson_score_interval(
            [bool(row["simple_grounding_check"]) for row in answerable],
            wide_interval_threshold=wide_interval_threshold,
        ),
        "status_accuracy": wilson_score_interval(
            [bool(row["status_correct"]) for row in rows],
            wide_interval_threshold=wide_interval_threshold,
        ),
    }
    if no_evidence:
        metrics["no_answer_accuracy"] = wilson_score_interval(
            [bool(row["no_answer_correct"]) for row in no_evidence],
            wide_interval_threshold=wide_interval_threshold,
        )
    if review_or_unsupported:
        metrics["review_or_unsupported_accuracy"] = wilson_score_interval(
            [bool(row["status_correct"]) for row in review_or_unsupported],
            wide_interval_threshold=wide_interval_threshold,
        )

    subgroups: dict[str, dict[str, object]] = {}
    for case_type in sorted({str(row["case_type"]) for row in answerable}):
        subgroup_rows = [row for row in answerable if row["case_type"] == case_type]
        subgroups[case_type] = {
            "sample_count": len(subgroup_rows),
            "retrieval_hit_at_1": wilson_score_interval(
                [
                    row.get("expected_source") in list(row.get("retrieved_sources", []))[:1]
                    for row in subgroup_rows
                ],
                wide_interval_threshold=wide_interval_threshold,
            ),
            "mean_reciprocal_rank": bootstrap_mean_interval(
                [float(row["reciprocal_rank"]) for row in subgroup_rows],
                resamples=resamples,
                seed=_derived_seed(seed, f"subgroup:{case_type}:mrr"),
                wide_interval_threshold=wide_interval_threshold,
            ),
        }

    mode_results = ablation_payload.get("results")
    if not isinstance(mode_results, dict) or candidate_mode not in mode_results:
        raise ValueError(f"Ablation payload is missing candidate mode '{candidate_mode}'.")
    paired_comparisons = [
        _paired_mode_comparison(
            candidate_mode=candidate_mode,
            baseline_mode=baseline_mode,
            candidate_payload=mode_results[candidate_mode],
            baseline_payload=baseline_payload,
            resamples=resamples,
            seed=seed,
            wide_interval_threshold=wide_interval_threshold,
        )
        for baseline_mode, baseline_payload in sorted(mode_results.items())
        if baseline_mode != candidate_mode
    ]
    paired_comparisons_by_baseline = {
        str(comparison["baseline_mode"]): comparison for comparison in paired_comparisons
    }

    return {
        "protocol": {
            "confidence_level": DEFAULT_CONFIDENCE_LEVEL,
            "bootstrap_resamples": resamples,
            "bootstrap_seed": seed,
            "wide_interval_threshold": wide_interval_threshold,
            "sampling_unit": "authored_evaluation_case",
            "interpretation": (
                "Intervals quantify case-resampling uncertainty inside this fixed authored "
                "evaluation set. They do not measure label independence, corpus currency, "
                "expert agreement, or performance on a broader query population."
            ),
        },
        "support": {
            "all_cases": len(rows),
            "answerable_cases": len(answerable),
            "no_evidence_cases": len(no_evidence),
            "review_or_unsupported_cases": len(review_or_unsupported),
        },
        "metrics": metrics,
        "answerable_case_type_metrics": subgroups,
        "paired_mode_comparisons": paired_comparisons,
        "paired_mode_comparisons_by_baseline": paired_comparisons_by_baseline,
    }
