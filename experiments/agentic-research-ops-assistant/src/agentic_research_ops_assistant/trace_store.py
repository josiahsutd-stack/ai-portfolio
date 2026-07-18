from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def default_trace_db(docs_dir: str | Path) -> Path:
    project_root = Path(docs_dir).resolve().parents[1]
    return project_root / ".artifacts" / "agent_traces.sqlite"


class SQLiteTraceStore:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _init(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_trace (
                    trace_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    task TEXT NOT NULL,
                    approval_required INTEGER NOT NULL,
                    trace_json TEXT NOT NULL,
                    eval_json TEXT NOT NULL
                )
                """)

    def save(
        self,
        *,
        trace_id: str,
        task: str,
        approval_required: bool,
        trace: dict[str, Any],
        evaluation: dict[str, Any],
    ) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO agent_trace
                    (trace_id, created_at, task, approval_required, trace_json, eval_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    trace_id,
                    utc_now(),
                    task,
                    int(approval_required),
                    json.dumps(trace, sort_keys=True),
                    json.dumps(evaluation, sort_keys=True),
                ),
            )

    def list_recent(self, *, limit: int = 20) -> list[dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT trace_id, created_at, task, approval_required, trace_json, eval_json
                FROM agent_trace
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            {
                "trace_id": row[0],
                "created_at": row[1],
                "task": row[2],
                "approval_required": bool(row[3]),
                "trace": json.loads(row[4]),
                "evaluation": json.loads(row[5]),
            }
            for row in rows
        ]


def evaluate_trace(trace: dict[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    if not trace.get("citations"):
        findings.append("missing_citations")
    if not trace.get("approval_required"):
        findings.append("missing_human_approval")
    tool_calls = trace.get("tool_calls", [])
    failed_tools = [
        call.get("name", "unknown")
        for call in tool_calls
        if call.get("status") not in {None, "ok", "denied"}
    ]
    if failed_tools:
        findings.append(f"failed_tools:{','.join(failed_tools)}")
    if "I could not find" in str(trace.get("final_report", "")) and trace.get("citations"):
        findings.append("conflicting_no_evidence_statement")
    return {
        "passed": not findings,
        "findings": findings,
        "tool_call_count": len(tool_calls),
        "citation_count": len(trace.get("citations", [])),
    }
