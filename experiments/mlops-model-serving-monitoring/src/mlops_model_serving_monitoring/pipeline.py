from __future__ import annotations

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

from .schemas import SCHEMA_VERSION, ChurnPredictionInput

FEATURES = ["tenure_months", "monthly_spend", "support_tickets", "usage_score"]


def generate_churn_data(rows: int = 160, seed: int = 12) -> pd.DataFrame:
    rng = pd.Series(range(rows)).sample(frac=1, random_state=seed).reset_index(drop=True)
    data = pd.DataFrame(
        {
            "tenure_months": (rng % 48) + 1,
            "monthly_spend": 20 + (rng % 80) * 1.7,
            "support_tickets": rng % 7,
            "usage_score": 0.2 + (rng % 100) / 125,
        }
    )
    data["churned"] = ((data["support_tickets"] > 4) | (data["usage_score"] < 0.35)).astype(int)
    return data


def train_churn_model(data: pd.DataFrame):
    train, test = train_test_split(data, test_size=0.25, random_state=3, stratify=data["churned"])
    model = RandomForestClassifier(n_estimators=80, random_state=4)
    model.fit(train[FEATURES], train["churned"])
    preds = model.predict(test[FEATURES])
    probabilities = model.predict_proba(test[FEATURES])[:, 1]
    return model, {
        "accuracy": round(float(accuracy_score(test["churned"], preds)), 3),
        "precision": round(float(precision_score(test["churned"], preds, zero_division=0)), 3),
        "recall": round(float(recall_score(test["churned"], preds, zero_division=0)), 3),
        "f1": round(float(f1_score(test["churned"], preds, zero_division=0)), 3),
        "roc_auc": round(float(roc_auc_score(test["churned"], probabilities)), 3),
        "brier_score": round(float(brier_score_loss(test["churned"], probabilities)), 3),
        "version": "demo-v2",
        "schema_version": SCHEMA_VERSION,
        "random_seed": 4,
        "features": FEATURES,
        "feature_schema": {feature: "numeric" for feature in FEATURES},
        "dataset_info": {
            "source": "synthetic generated churn data",
            "label": "churned",
            "row_count": int(len(data)),
        },
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
    }


def predict_churn(model, payload: dict[str, float]) -> dict[str, float]:
    try:
        validated = ChurnPredictionInput.model_validate(payload)
    except Exception as exc:
        raise ValueError(f"Invalid prediction payload: {exc}") from exc
    request = validated.model_dump()
    frame = pd.DataFrame([request])
    probability = float(model.predict_proba(frame[FEATURES])[0][1])
    return {
        "churn_probability": round(probability, 3),
        "predicted_label": int(probability >= 0.5),
        "schema_version": SCHEMA_VERSION,
        "warnings": [],
    }
