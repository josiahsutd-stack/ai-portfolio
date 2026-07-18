from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

NUMERIC_FEATURES = [
    "week",
    "foundation_pct",
    "structure_pct",
    "envelope_pct",
    "mep_pct",
    "interior_pct",
    "handover_pct",
    "safety_observations",
    "weather_delay_days",
]
CATEGORICAL_FEATURES = ["zone"]
TARGET = "stage_label"


def load_metadata(path: str | Path) -> pd.DataFrame:
    data = pd.read_csv(path)
    if data.empty:
        raise ValueError("Progress metadata is empty.")
    return data


def _pipeline() -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("categorical", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
            ("numeric", "passthrough", NUMERIC_FEATURES),
        ]
    )
    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "model",
                RandomForestClassifier(n_estimators=80, random_state=7, class_weight="balanced"),
            ),
        ]
    )


def train_stage_classifier(data: pd.DataFrame) -> Pipeline:
    missing = set(NUMERIC_FEATURES + CATEGORICAL_FEATURES + [TARGET]) - set(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    model = _pipeline()
    model.fit(data[NUMERIC_FEATURES + CATEGORICAL_FEATURES], data[TARGET])
    return model


def evaluate_classifier(data: pd.DataFrame) -> dict[str, Any]:
    train, test = train_test_split(data, test_size=0.25, random_state=11, stratify=data[TARGET])
    model = train_stage_classifier(train)
    predictions = model.predict(test[NUMERIC_FEATURES + CATEGORICAL_FEATURES])
    return {
        "accuracy": round(float(accuracy_score(test[TARGET], predictions)), 3),
        "report": classification_report(test[TARGET], predictions, zero_division=0),
    }


def predict_stage(model: Pipeline, observation: dict[str, Any]) -> str:
    frame = pd.DataFrame([observation])
    return str(model.predict(frame[NUMERIC_FEATURES + CATEGORICAL_FEATURES])[0])
