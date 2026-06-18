from __future__ import annotations

from math import log
from typing import Any

import pandas as pd


def population_stability_index(
    reference: pd.Series,
    current: pd.Series,
    *,
    bins: int = 10,
) -> float:
    ref = pd.to_numeric(reference, errors="coerce").dropna()
    cur = pd.to_numeric(current, errors="coerce").dropna()
    if ref.empty or cur.empty:
        return 0.0
    quantiles = ref.quantile([idx / bins for idx in range(bins + 1)]).drop_duplicates()
    if len(quantiles) < 3:
        quantiles = pd.Series([min(ref.min(), cur.min()), max(ref.max(), cur.max())])
    edges = sorted(set(float(value) for value in quantiles.tolist()))
    if len(edges) < 2 or edges[0] == edges[-1]:
        return 0.0
    edges[0] = min(edges[0], float(cur.min())) - 1e-9
    edges[-1] = max(edges[-1], float(cur.max())) + 1e-9
    ref_counts = pd.cut(ref, edges, include_lowest=True).value_counts(sort=False)
    cur_counts = pd.cut(cur, edges, include_lowest=True).value_counts(sort=False)
    ref_pct = ref_counts / max(1, ref_counts.sum())
    cur_pct = cur_counts / max(1, cur_counts.sum())
    psi = 0.0
    for ref_value, cur_value in zip(ref_pct, cur_pct, strict=False):
        psi += (cur_value - ref_value) * log((cur_value + 1e-6) / (ref_value + 1e-6))
    return round(float(abs(psi)), 4)


def detect_drift(
    reference: pd.DataFrame, current: pd.DataFrame, threshold: float = 0.2
) -> dict[str, object]:
    drifted: list[str] = []
    scores: dict[str, dict[str, float]] = {}
    for column in reference.select_dtypes("number").columns:
        if column not in current:
            continue
        ref_mean = float(reference[column].mean())
        cur_mean = float(current[column].mean())
        mean_shift = abs(cur_mean - ref_mean) / max(1.0, abs(ref_mean))
        psi = population_stability_index(reference[column], current[column])
        scores[column] = {"mean_shift": round(mean_shift, 3), "psi": psi}
        if mean_shift > threshold or psi > threshold:
            drifted.append(column)
    return {"drifted_features": drifted, "scores": scores, "drift_detected": bool(drifted)}


def generate_monitoring_report(
    reference: pd.DataFrame,
    current: pd.DataFrame,
    *,
    prediction_logs: list[dict[str, Any]] | None = None,
    drift_threshold: float = 0.2,
) -> dict[str, Any]:
    logs = prediction_logs or []
    drift = detect_drift(reference, current, threshold=drift_threshold)
    latencies = [
        int(log["latency_ms"])
        for log in logs
        if log.get("latency_ms") is not None and str(log.get("latency_ms")).isdigit()
    ]
    return {
        "report_type": "local_synthetic_monitoring_report",
        "drift_threshold": drift_threshold,
        "prediction_volume": len(logs),
        "latency_ms": {
            "count": len(latencies),
            "avg": round(sum(latencies) / len(latencies), 2) if latencies else None,
            "max": max(latencies) if latencies else None,
        },
        "error_count": sum(1 for log in logs if log.get("error_text")),
        "drift": drift,
        "warnings": [f"Drift detected for {feature}" for feature in drift["drifted_features"]],
    }
