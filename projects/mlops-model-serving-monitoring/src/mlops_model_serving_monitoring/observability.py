from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_registry_dir() -> Path:
    return project_root() / ".artifacts" / "model_registry"


def default_db_path() -> Path:
    return default_registry_dir() / "inference_log.sqlite"


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def save_model_artifact(
    model: Any,
    metrics: dict[str, Any],
    *,
    registry_dir: str | Path | None = None,
) -> dict[str, str]:
    target = Path(registry_dir) if registry_dir else default_registry_dir()
    target.mkdir(parents=True, exist_ok=True)
    version = str(metrics.get("version", "demo-v1"))
    model_path = target / f"churn_model_{version}.joblib"
    metadata_path = target / f"churn_model_{version}.json"
    joblib.dump(model, model_path)
    metadata = {
        "version": version,
        "saved_at": utc_now(),
        "metrics": metrics,
        "artifact": model_path.name,
    }
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return {"model_path": str(model_path), "metadata_path": str(metadata_path)}


def load_model_artifact(model_path: str | Path) -> Any:
    return joblib.load(model_path)


def init_observability_db(db_path: str | Path | None = None) -> Path:
    target = Path(db_path) if db_path else default_db_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(target) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS prediction_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                model_version TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                prediction_json TEXT NOT NULL
            )
            """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS drift_report (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                reference_window TEXT NOT NULL,
                current_window TEXT NOT NULL,
                drift_detected INTEGER NOT NULL,
                report_json TEXT NOT NULL
            )
            """)
    return target


def log_prediction(
    payload: dict[str, float],
    prediction: dict[str, float],
    *,
    model_version: str,
    db_path: str | Path | None = None,
) -> int:
    target = init_observability_db(db_path)
    with sqlite3.connect(target) as conn:
        cursor = conn.execute(
            """
            INSERT INTO prediction_log
                (created_at, model_version, payload_json, prediction_json)
            VALUES (?, ?, ?, ?)
            """,
            (
                utc_now(),
                model_version,
                json.dumps(payload, sort_keys=True),
                json.dumps(prediction, sort_keys=True),
            ),
        )
        return int(cursor.lastrowid)


def list_prediction_logs(
    *, limit: int = 20, db_path: str | Path | None = None
) -> list[dict[str, Any]]:
    target = init_observability_db(db_path)
    with sqlite3.connect(target) as conn:
        rows = conn.execute(
            """
            SELECT id, created_at, model_version, payload_json, prediction_json
            FROM prediction_log
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [
        {
            "id": row[0],
            "created_at": row[1],
            "model_version": row[2],
            "payload": json.loads(row[3]),
            "prediction": json.loads(row[4]),
        }
        for row in rows
    ]


def record_drift_report(
    report: dict[str, Any],
    *,
    reference_window: str,
    current_window: str,
    db_path: str | Path | None = None,
) -> int:
    target = init_observability_db(db_path)
    with sqlite3.connect(target) as conn:
        cursor = conn.execute(
            """
            INSERT INTO drift_report
                (created_at, reference_window, current_window, drift_detected, report_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                utc_now(),
                reference_window,
                current_window,
                int(bool(report.get("drift_detected"))),
                json.dumps(report, sort_keys=True),
            ),
        )
        return int(cursor.lastrowid)


def list_drift_reports(
    *, limit: int = 20, db_path: str | Path | None = None
) -> list[dict[str, Any]]:
    target = init_observability_db(db_path)
    with sqlite3.connect(target) as conn:
        rows = conn.execute(
            """
            SELECT id, created_at, reference_window, current_window, drift_detected, report_json
            FROM drift_report
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [
        {
            "id": row[0],
            "created_at": row[1],
            "reference_window": row[2],
            "current_window": row[3],
            "drift_detected": bool(row[4]),
            "report": json.loads(row[5]),
        }
        for row in rows
    ]
