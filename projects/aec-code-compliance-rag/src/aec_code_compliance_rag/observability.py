from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from math import ceil
from pathlib import Path
from typing import Any


def _connect(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path, timeout=5.0)
    connection.execute("PRAGMA busy_timeout = 5000")
    return connection


class QueryLogger:
    def __init__(self, path: str | Path, *, store_payloads: bool = False) -> None:
        self.path = Path(path)
        self.store_payloads = store_payloads
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with _connect(self.path) as connection:
            connection.execute("PRAGMA journal_mode = WAL")
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
        with _connect(self.path) as connection:
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
        with _connect(self.path) as connection:
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


class ServiceTelemetryStore:
    """Bounded request telemetry without arbitrary headers, query strings, or payloads."""

    def __init__(self, path: str | Path, *, retention: int = 5000) -> None:
        if retention < 1:
            raise ValueError("retention must be at least 1")
        self.path = Path(path)
        self.retention = retention
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with _connect(self.path) as connection:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.execute("""
                CREATE TABLE IF NOT EXISTS service_request (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    instance_id TEXT NOT NULL,
                    request_id TEXT NOT NULL,
                    method TEXT NOT NULL,
                    route TEXT NOT NULL,
                    status_code INTEGER NOT NULL,
                    latency_ms REAL NOT NULL
                )
                """)
            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_service_request_route
                ON service_request(method, route, id DESC)
                """)

    def record(
        self,
        *,
        instance_id: str,
        request_id: str,
        method: str,
        route: str,
        status_code: int,
        latency_ms: float,
    ) -> None:
        with _connect(self.path) as connection:
            connection.execute(
                """
                INSERT INTO service_request (
                    created_at,
                    instance_id,
                    request_id,
                    method,
                    route,
                    status_code,
                    latency_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.now(UTC).isoformat(),
                    instance_id,
                    request_id,
                    method.upper(),
                    route,
                    int(status_code),
                    max(0.0, float(latency_ms)),
                ),
            )
            connection.execute(
                """
                DELETE FROM service_request
                WHERE id <= COALESCE(
                    (
                        SELECT id
                        FROM service_request
                        ORDER BY id DESC
                        LIMIT 1 OFFSET ?
                    ),
                    -1
                )
                """,
                (self.retention,),
            )

    def snapshot(
        self,
        *,
        limit: int = 200,
        route: str | None = None,
    ) -> dict[str, object]:
        if limit < 1:
            raise ValueError("limit must be at least 1")
        where_clause = ""
        parameters: list[object] = []
        if route is not None:
            method, separator, route_path = route.partition(" ")
            if not separator or not method or not route_path:
                raise ValueError("route must use the form `METHOD /path`")
            where_clause = "WHERE method = ? AND route = ?"
            parameters.extend([method.upper(), route_path])
        with _connect(self.path) as connection:
            connection.row_factory = sqlite3.Row
            retained_request_count = int(
                connection.execute("SELECT COUNT(*) FROM service_request").fetchone()[0]
            )
            rows = connection.execute(
                f"""
                SELECT method, route, status_code, latency_ms
                FROM service_request
                {where_clause}
                ORDER BY id DESC
                LIMIT ?
                """,
                (*parameters, limit),
            ).fetchall()

        latencies = sorted(float(row["latency_ms"]) for row in rows)
        status_counts: dict[str, int] = {}
        route_counts: dict[str, int] = {}
        for row in rows:
            status = str(row["status_code"])
            route_name = f"{row['method']} {row['route']}"
            status_counts[status] = status_counts.get(status, 0) + 1
            route_counts[route_name] = route_counts.get(route_name, 0) + 1
        sample_count = len(rows)
        p95_index = max(0, ceil(sample_count * 0.95) - 1)
        p95 = latencies[p95_index] if latencies else 0.0
        client_errors = sum(
            count for status, count in status_counts.items() if 400 <= int(status) < 500
        )
        server_errors = sum(count for status, count in status_counts.items() if int(status) >= 500)
        return {
            "storage": "sqlite",
            "payloads_stored": False,
            "retention_limit": self.retention,
            "retained_request_count": retained_request_count,
            "window_limit": limit,
            "window_request_count": sample_count,
            "route_filter": route,
            "client_error_count": client_errors,
            "server_error_count": server_errors,
            "client_error_rate": round(client_errors / sample_count, 6) if sample_count else 0.0,
            "server_error_rate": round(server_errors / sample_count, 6) if sample_count else 0.0,
            "average_latency_ms": round(sum(latencies) / sample_count, 3) if sample_count else 0.0,
            "p95_latency_ms": round(p95, 3),
            "requests_by_route": dict(sorted(route_counts.items())),
            "responses_by_status": dict(sorted(status_counts.items())),
        }
