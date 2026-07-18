from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import mean_absolute_error, mean_squared_error


def generate_series(periods: int = 96, seed: int = 8) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    index = np.arange(periods)
    values = 120 + 18 * np.sin(index / 6) + rng.normal(0, 4, periods)
    anomaly_points = [28, 64, 81]
    for point in anomaly_points:
        if point < periods:
            values[point] += 55
    return pd.DataFrame(
        {"t": index, "value": values, "is_anomaly": [i in anomaly_points for i in index]}
    )


def forecast_moving_average(data: pd.DataFrame, window: int = 6) -> pd.Series:
    return data["value"].rolling(window=window, min_periods=1).mean().shift(1).bfill()


def detect_anomalies(data: pd.DataFrame) -> pd.DataFrame:
    model = IsolationForest(contamination=0.08, random_state=4)
    labels = model.fit_predict(data[["value"]])
    result = data.copy()
    result["predicted_anomaly"] = labels == -1
    return result


def regression_forecast_metrics(actual: pd.Series, forecast: pd.Series) -> dict[str, float]:
    mae = mean_absolute_error(actual, forecast)
    rmse = mean_squared_error(actual, forecast) ** 0.5
    mape = float((abs((actual - forecast) / actual.clip(lower=1))).mean())
    return {"mae": round(float(mae), 3), "rmse": round(float(rmse), 3), "mape": round(mape, 3)}
