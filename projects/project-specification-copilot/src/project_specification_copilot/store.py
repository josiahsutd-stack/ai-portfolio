from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .models import AuditEvent


class AuditStore:
    def __init__(self, path: str | Path = ":memory:") -> None:
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS audit_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
            """)
        self.connection.commit()

    def append(self, event_type: str, payload: dict[str, Any]) -> AuditEvent:
        serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        cursor = self.connection.execute(
            "INSERT INTO audit_events (event_type, payload_json) VALUES (?, ?)",
            (event_type, serialized),
        )
        self.connection.commit()
        return AuditEvent(int(cursor.lastrowid), event_type, payload)

    def events(self) -> list[AuditEvent]:
        rows = self.connection.execute(
            "SELECT event_id, event_type, payload_json FROM audit_events ORDER BY event_id"
        ).fetchall()
        return [
            AuditEvent(int(event_id), str(event_type), json.loads(payload_json))
            for event_id, event_type, payload_json in rows
        ]

    def close(self) -> None:
        self.connection.close()
