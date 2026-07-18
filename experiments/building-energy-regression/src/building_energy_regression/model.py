from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

TARGET = "energy_use_kwh_m2_year"
CATEGORICAL_FEATURES = ["building_type", "orientation", "climate_zone", "hvac_type"]
NUMERIC_FEATURES = [
    "floor_area_m2",
    "glazing_ratio",
    "occupancy",
    "insulation_score",
    "operating_hours_per_week",
]
ENERGY_FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES
EVALUATION_TEST_SIZE = 0.25
EVALUATION_RANDOM_STATE = 13


def load_energy_data(path: str | Path) -> pd.DataFrame:
    data = pd.read_csv(path)
    if data.empty:
        raise ValueError("Energy dataset is empty.")
    return data


def _pipeline() -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("categorical", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
            ("numeric", StandardScaler(), NUMERIC_FEATURES),
        ]
    )
    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", RandomForestRegressor(n_estimators=120, random_state=9, min_samples_leaf=3)),
        ]
    )


def _validate_energy_data(data: pd.DataFrame) -> None:
    if data.empty:
        raise ValueError("Energy dataset is empty.")
    missing = set(ENERGY_FEATURES + [TARGET]) - set(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")


def train_energy_model(data: pd.DataFrame) -> Pipeline:
    _validate_energy_data(data)
    model = _pipeline()
    model.fit(data[ENERGY_FEATURES], data[TARGET])
    return model


def _regression_metrics(actual: pd.Series, predicted: object) -> dict[str, float]:
    return {
        "mae": round(float(mean_absolute_error(actual, predicted)), 2),
        "r2": round(float(r2_score(actual, predicted)), 3),
    }


def evaluate_energy_model_detailed(data: pd.DataFrame) -> dict[str, object]:
    """Evaluate the model and a mean baseline on one fixed synthetic holdout split."""
    _validate_energy_data(data)
    train, test = train_test_split(
        data,
        test_size=EVALUATION_TEST_SIZE,
        random_state=EVALUATION_RANDOM_STATE,
    )
    model = train_energy_model(train)
    predictions = model.predict(test[ENERGY_FEATURES])

    baseline = DummyRegressor(strategy="mean")
    baseline.fit(train[ENERGY_FEATURES], train[TARGET])
    baseline_predictions = baseline.predict(test[ENERGY_FEATURES])

    model_metrics = _regression_metrics(test[TARGET], predictions)
    baseline_metrics = _regression_metrics(test[TARGET], baseline_predictions)
    example_position = 0
    example_actual = float(test[TARGET].iloc[example_position])
    example_prediction = float(predictions[example_position])
    baseline_mae = baseline_metrics["mae"]
    mae_reduction = (
        round((baseline_mae - model_metrics["mae"]) / baseline_mae, 3) if baseline_mae else 0.0
    )

    return {
        "artifact_schema_version": 1,
        "data_status": "synthetic",
        "evaluation_scope": "fixed holdout split of bundled synthetic rows",
        "dataset": {
            "row_count": len(data),
            "target": TARGET,
        },
        "split": {
            "train_rows": len(train),
            "test_rows": len(test),
            "test_fraction": EVALUATION_TEST_SIZE,
            "random_state": EVALUATION_RANDOM_STATE,
        },
        "model": {
            "name": "random_forest_regressor",
            "metrics": model_metrics,
        },
        "baseline": {
            "name": "training_target_mean",
            "metrics": baseline_metrics,
        },
        "comparison": {
            "mae_reduction_fraction_vs_mean_baseline": mae_reduction,
        },
        "holdout_example": {
            "source_row_index": int(test.index[example_position]),
            "actual_kwh_m2_year": round(example_actual, 2),
            "predicted_kwh_m2_year": round(example_prediction, 2),
            "absolute_error_kwh_m2_year": round(abs(example_actual - example_prediction), 2),
        },
    }


def evaluate_energy_model(data: pd.DataFrame) -> dict[str, float]:
    details = evaluate_energy_model_detailed(data)
    return dict(details["model"]["metrics"])


def predict_energy_use(model: Pipeline, features: dict[str, Any]) -> float:
    frame = pd.DataFrame([features])
    missing = set(ENERGY_FEATURES) - set(frame.columns)
    if missing:
        raise ValueError(f"Missing prediction fields: {sorted(missing)}")
    return round(float(model.predict(frame[ENERGY_FEATURES])[0]), 2)
