from __future__ import annotations

import json
from pathlib import Path

from .chunking import DOCUMENT_METADATA_FIELDS


def _metadata_key(raw_key: str) -> str:
    return raw_key.strip().lower().replace(" ", "_").replace("-", "_")


def _metadata_value(key: str, value: object) -> str:
    if key == "superseded" and isinstance(value, bool):
        return str(value).lower()
    return str(value).strip()


def load_source_manifest(path: str | Path) -> dict[str, dict[str, object]]:
    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))
    rows = payload.get("sources", payload) if isinstance(payload, dict) else payload
    manifest: dict[str, dict[str, object]] = {}
    for row in rows:
        source = str(row["source"])
        record: dict[str, object] = {"source": source}
        for raw_key, raw_value in row.items():
            key = _metadata_key(str(raw_key))
            if key in DOCUMENT_METADATA_FIELDS and raw_value is not None:
                record[key] = _metadata_value(key, raw_value)
        manifest[source] = record
    return manifest


def default_source_manifest_path(paths: list[str | Path]) -> Path | None:
    parents = {Path(path).parent.resolve() for path in paths}
    if len(parents) != 1:
        return None
    candidate = next(iter(parents)) / "source_manifest.json"
    return candidate if candidate.exists() else None
