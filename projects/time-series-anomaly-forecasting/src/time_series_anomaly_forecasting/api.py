from __future__ import annotations

from fastapi import FastAPI

from .timeseries import (
    detect_anomalies,
    forecast_moving_average,
    generate_series,
    regression_forecast_metrics,
)

app = FastAPI(title="Time-Series Forecast and Anomaly Baselines")


@app.get("/forecast")
def forecast() -> dict[str, object]:
    data = generate_series()
    forecast_values = forecast_moving_average(data)
    detected = detect_anomalies(data)
    return {
        "metrics": regression_forecast_metrics(data["value"], forecast_values),
        "alert_count": int(detected["predicted_anomaly"].sum()),
    }
