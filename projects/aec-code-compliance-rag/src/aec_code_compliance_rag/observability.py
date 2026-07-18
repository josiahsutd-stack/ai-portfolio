from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class QueryLogger:
    def __init__(self, path: str | Path, *, store_payloads: bool = False) -> None:
        self.path = Path(path)
        self.store_payloads = store_payloads
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with sqlite3.connect(self.path) as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS query_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    corpus TEXT NOT NULL,
                    retrieval_mode TEXT NOT NULL,
                    question TEXT NOT NULL,
                    status TEXT NOT NULL,
                    confidence TEXT NOT NULL,
                    result_count INTEGER NOT NULL,
                    latency_ms INTEGER NOT NULL,
                    source_filters_json TEXT NOT NULL,
                    response_json TEXT NOT NULL
                )
                """)
            columns = {
                str(row[1]) for row in connection.execute("PRAGMA table_info(query_log)").fetchall()
            }
            migrations = {
                "request_id": "TEXT NOT NULL DEFAULT ''",
                "operation": "TEXT NOT NULL DEFAULT 'query'",
                "error_type": "TEXT NOT NULL DEFAULT ''",
            }
            for column, definition in migrations.items():
                if column not in columns:
                    connection.execute(f"ALTER TABLE query_log ADD COLUMN {column} {definition}")

    def log_query(
        self,
        *,
        corpus: str,
        retrieval_mode: str,
        question: str,
        response: dict[str, Any],
        latency_ms: int,
        source_filters: dict[str, Any] | None = None,
        request_id: str = "",
        operation: str = "query",
        error_type: str = "",
    ) -> int:
        retrieval = response.get("retrieval", {})
        stored_question = question if self.store_payloads else "[redacted]"
        stored_response = (
            response
            if self.store_payloads
            else {
                "status": response.get("status", ""),
                "confidence": response.get("confidence", ""),
                "result_count": retrieval.get("result_count", 0),
            }
        )
        with sqlite3.connect(self.path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO query_log (
                    created_at,
                    corpus,
                    retrieval_mode,
                    question,
                    status,
                    confidence,
                    result_count,
                    latency_ms,
                    source_filters_json,
                    response_json,
                    request_id,
                    operation,
                    error_type
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.now(UTC).isoformat(),
                    corpus,
                    retrieval_mode,
                    stored_question,
                    str(response.get("status", "")),
                    str(response.get("confidence", "")),
                    int(retrieval.get("result_count", 0)),
                    latency_ms,
                    json.dumps(source_filters or {}, sort_keys=True),
                    json.dumps(stored_response, sort_keys=True, default=str),
                    request_id,
                    operation,
                    error_type,
                ),
            )
            return int(cursor.lastrowid)

    def recent(self, *, limit: int = 20) -> list[dict[str, Any]]:
        with sqlite3.connect(self.path) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                """
                SELECT id, created_at, corpus, retrieval_mode, question, status,
                       confidence, result_count, latency_ms, source_filters_json,
                       response_json, request_id, operation, error_type
                FROM query_log
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        records = [dict(row) for row in rows]
        for record in records:
            record["source_filters"] = json.loads(record["source_filters_json"])
            record["response"] = json.loads(record["response_json"])
        return records
