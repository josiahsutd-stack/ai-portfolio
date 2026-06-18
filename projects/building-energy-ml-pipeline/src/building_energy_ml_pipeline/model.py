from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.compose import ColumnTransformer
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


def train_energy_model(data: pd.DataFrame) -> Pipeline:
    missing = set(ENERGY_FEATURES + [TARGET]) - set(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    model = _pipeline()
    model.fit(data[ENERGY_FEATURES], data[TARGET])
    return model


def evaluate_energy_model(data: pd.DataFrame) -> dict[str, float]:
    train, test = train_test_split(data, test_size=0.25, random_state=13)
    model = train_energy_model(train)
    predictions = model.predict(test[ENERGY_FEATURES])
    return {
        "mae": round(float(mean_absolute_error(test[TARGET], predictions)), 2),
        "r2": round(float(r2_score(test[TARGET], predictions)), 3),
    }


def predict_energy_use(model: Pipeline, features: dict[str, Any]) -> float:
    frame = pd.DataFrame([features])
    missing = set(ENERGY_FEATURES) - set(frame.columns)
    if missing:
        raise ValueError(f"Missing prediction fields: {sorted(missing)}")
    return round(float(model.predict(frame[ENERGY_FEATURES])[0]), 2)
