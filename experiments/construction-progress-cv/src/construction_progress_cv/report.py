from __future__ import annotations

import pandas as pd


def build_progress_summary(data: pd.DataFrame) -> str:
    if data.empty:
        return "No construction progress observations are available."
    latest = data.sort_values("week").iloc[-1]
    progress_fields = [
        "foundation_pct",
        "structure_pct",
        "envelope_pct",
        "mep_pct",
        "interior_pct",
        "handover_pct",
    ]
    strongest = max(progress_fields, key=lambda field: float(latest[field]))
    weakest = min(progress_fields, key=lambda field: float(latest[field]))
    risks = []
    if int(latest["weather_delay_days"]) > 0:
        risks.append(f"{int(latest['weather_delay_days'])} weather-delay day(s)")
    if int(latest["safety_observations"]) >= 3:
        risks.append("elevated safety observations")
    risk_text = "; ".join(risks) if risks else "no major synthetic risk flags"
    return (
        f"Week {int(latest['week'])} is classified as `{latest['stage_label']}` for the "
        f"{latest['zone']} zone. Strongest progress signal: `{strongest}` at "
        f"{float(latest[strongest]):.1f}%. Weakest signal: `{weakest}` at "
        f"{float(latest[weakest]):.1f}%. Risk notes: {risk_text}."
    )
