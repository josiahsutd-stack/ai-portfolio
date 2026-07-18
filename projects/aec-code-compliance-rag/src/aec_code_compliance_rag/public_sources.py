from __future__ import annotations

import hashlib
import json
import re
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


class _VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._skip_depth = 0
        self._parts: list[str] = []
        self._current_href: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript", "svg"}:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        if tag in {"h1", "h2", "h3"}:
            self._parts.append("\n\n## ")
        elif tag in {"p", "li", "tr", "div", "section", "article"}:
            self._parts.append("\n")
        elif tag == "a":
            href = dict(attrs).get("href")
            self._current_href = href

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript", "svg"} and self._skip_depth:
            self._skip_depth -= 1
        if tag == "a":
            self._current_href = None

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        text = " ".join(data.split())
        if not text:
            return
        if self._current_href and self._current_href.startswith(("http://", "https://")):
            text = f"{text} ({self._current_href})"
        self._parts.append(text)
        self._parts.append(" ")

    def text(self) -> str:
        raw_text = "".join(self._parts)
        raw_text = re.sub(r"[ \t]+", " ", raw_text)
        raw_text = re.sub(r"\n{3,}", "\n\n", raw_text)
        return raw_text.strip()


@dataclass(frozen=True)
class DownloadedSource:
    source: str
    path: Path
    bytes_written: int
    content_type: str
    url: str
    sha256: str


def public_sources_root(project_root: str | Path | None = None) -> Path:
    if project_root is not None:
        return Path(project_root) / "public_sources"
    return Path(__file__).resolve().parents[2] / "public_sources"


def load_public_source_definitions(
    source_file: str | Path | None = None,
) -> dict[str, Any]:
    target = Path(source_file) if source_file else public_sources_root() / "sources.json"
    payload = json.loads(target.read_text(encoding="utf-8"))
    _validate_source_definitions(payload)
    return payload


def public_download_dir(source_file: str | Path | None = None) -> Path:
    source_path = Path(source_file) if source_file else public_sources_root() / "sources.json"
    payload = load_public_source_definitions(source_path)
    return source_path.parent / str(payload.get("download_dir", "downloaded"))


def downloaded_public_paths(download_dir: str | Path | None = None) -> list[Path]:
    target = Path(download_dir) if download_dir else public_download_dir()
    if not target.exists():
        return []
    manifest_path = target / "source_manifest.json"
    if manifest_path.exists():
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        return [
            target / str(row["source"])
            for row in payload.get("sources", [])
            if (target / str(row["source"])).is_file()
        ]
    return sorted([*target.glob("*.pdf"), *target.glob("*.md")])


def download_public_sources(
    source_file: str | Path | None = None,
    *,
    force: bool = False,
    timeout_seconds: int = 90,
) -> dict[str, Any]:
    source_path = Path(source_file) if source_file else public_sources_root() / "sources.json"
    payload = load_public_source_definitions(source_path)
    source_inventory_sha256 = _canonical_sha256(payload.get("sources", []))
    download_dir = source_path.parent / str(payload.get("download_dir", "downloaded"))
    download_dir.mkdir(parents=True, exist_ok=True)

    downloaded_at = datetime.now(UTC).isoformat()
    records: list[DownloadedSource] = []
    manifest_rows: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    for row in payload.get("sources", []):
        source_name = str(row["source"])
        destination = download_dir / source_name
        try:
            record = _download_one(
                row,
                destination=destination,
                force=force,
                timeout_seconds=timeout_seconds,
            )
            records.append(record)
            manifest_rows.append(
                {
                    **{
                        key: value
                        for key, value in row.items()
                        if key
                        in {
                            "source",
                            "title",
                            "publisher",
                            "source_url",
                            "source_type",
                            "jurisdiction",
                            "code_year",
                            "document_version",
                            "superseded",
                            "allowed_use",
                            "rights",
                            "source_note",
                            "document_id",
                            "landing_page",
                        }
                    },
                    "downloaded_at": downloaded_at,
                    "source": source_name,
                    "resolved_url": record.url,
                    "content_type": record.content_type,
                    "bytes": record.bytes_written,
                    "sha256": record.sha256,
                }
            )
        except Exception as exc:  # pragma: no cover - network failures vary
            failures.append({"source": source_name, "error": str(exc)})

    corpus_sha256 = _corpus_sha256(records)
    manifest_payload = {
        "schema_version": "2.0",
        "note": "Generated from public_sources/sources.json. Downloaded files are local-only and not committed.",
        "generated_at": downloaded_at,
        "source_inventory_sha256": source_inventory_sha256,
        "corpus_sha256": corpus_sha256,
        "document_count": len(records),
        "failed_source_count": len(failures),
        "is_complete": not failures and len(records) == len(payload.get("sources", [])),
        "sources": manifest_rows,
    }
    _write_json(download_dir / "source_manifest.json", manifest_payload)
    report = {
        "schema_version": "2.0",
        "generated_at": downloaded_at,
        "download_dir": str(download_dir),
        "source_inventory_sha256": source_inventory_sha256,
        "corpus_sha256": corpus_sha256,
        "is_complete": manifest_payload["is_complete"],
        "downloaded_count": len(records),
        "failure_count": len(failures),
        "downloaded": [
            {
                "source": record.source,
                "path": str(record.path),
                "bytes_written": record.bytes_written,
                "content_type": record.content_type,
                "url": record.url,
                "sha256": record.sha256,
            }
            for record in records
        ],
        "failures": failures,
    }
    _write_json(source_path.parent / "download_report.json", report)
    return report


def _download_one(
    row: dict[str, Any],
    *,
    destination: Path,
    force: bool,
    timeout_seconds: int,
) -> DownloadedSource:
    source_url = str(row["source_url"])
    if destination.exists() and not force:
        body = destination.read_bytes()
        content_type = _existing_content_type(destination)
        _validate_download_body(
            body,
            source_name=destination.name,
            content_type=content_type,
            final_url=source_url,
        )
        return DownloadedSource(
            source=destination.name,
            path=destination,
            bytes_written=destination.stat().st_size,
            content_type=content_type,
            url=source_url,
            sha256=_sha256_bytes(body),
        )

    request = urllib.request.Request(
        source_url,
        headers={"User-Agent": "ai-portfolio-local-review/1.0"},
    )
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        status = int(getattr(response, "status", 200))
        content_type = response.headers.get("content-type", "")
        body = response.read()
        final_url = response.geturl()
    if status >= 400:
        raise ValueError(f"HTTP {status} returned for {source_url}")
    _validate_download_body(
        body,
        source_name=destination.name,
        content_type=content_type,
        final_url=final_url,
    )

    temporary = destination.with_name(f"{destination.name}.part")
    if destination.suffix.lower() == ".md":
        text = _html_to_markdown(body.decode("utf-8", errors="replace"), row)
        temporary.write_text(text, encoding="utf-8")
    else:
        temporary.write_bytes(body)
    temporary.replace(destination)
    stored_body = destination.read_bytes()
    return DownloadedSource(
        source=destination.name,
        path=destination,
        bytes_written=destination.stat().st_size,
        content_type=content_type,
        url=final_url,
        sha256=_sha256_bytes(stored_body),
    )


def _validate_source_definitions(payload: dict[str, Any]) -> None:
    rows = payload.get("sources")
    if not isinstance(rows, list) or not rows:
        raise ValueError("Public source inventory must contain a non-empty 'sources' list.")
    required = {
        "source",
        "title",
        "publisher",
        "source_url",
        "source_type",
        "jurisdiction",
        "document_version",
        "allowed_use",
        "rights",
    }
    seen_sources: set[str] = set()
    seen_document_ids: set[str] = set()
    for index, row in enumerate(rows, start=1):
        missing = sorted(required - row.keys())
        if missing:
            raise ValueError(f"Public source row {index} is missing: {', '.join(missing)}")
        source = str(row["source"])
        document_id = str(row.get("document_id", Path(source).stem))
        if source in seen_sources:
            raise ValueError(f"Duplicate public source filename: {source}")
        if document_id in seen_document_ids:
            raise ValueError(f"Duplicate public source document_id: {document_id}")
        seen_sources.add(source)
        seen_document_ids.add(document_id)
        source_type = str(row["source_type"]).lower()
        expected_suffix = ".pdf" if source_type == "pdf" else ".md" if source_type == "html" else ""
        if not expected_suffix or Path(source).suffix.lower() != expected_suffix:
            raise ValueError(
                f"Source {source} has source_type={source_type!r}; expected a matching PDF or HTML/Markdown filename."
            )
        if not str(row["source_url"]).startswith("https://"):
            raise ValueError(f"Source {source} must use an HTTPS source_url.")


def _validate_download_body(
    body: bytes,
    *,
    source_name: str,
    content_type: str,
    final_url: str,
) -> None:
    if len(body) < 64:
        raise ValueError(f"Downloaded payload for {source_name} is unexpectedly small.")
    suffix = Path(source_name).suffix.lower()
    normalized_type = content_type.lower()
    if suffix == ".pdf":
        if not body.lstrip().startswith(b"%PDF-"):
            raise ValueError(
                f"Expected PDF for {source_name}, received {content_type or 'unknown content type'} from {final_url}."
            )
        if "html" in normalized_type:
            raise ValueError(f"Expected PDF for {source_name}, received HTML from {final_url}.")
        return
    if suffix == ".md":
        prefix = body[:2048].lower()
        if body.lstrip().startswith(b"%PDF-"):
            raise ValueError(f"Expected HTML for {source_name}, received a PDF from {final_url}.")
        if "markdown" in normalized_type:
            return
        if (
            "html" not in normalized_type
            and b"<html" not in prefix
            and b"<!doctype html" not in prefix
        ):
            raise ValueError(
                f"Expected HTML for {source_name}, received {content_type or 'unknown content type'} from {final_url}."
            )


def _existing_content_type(path: Path) -> str:
    return "application/pdf" if path.suffix.lower() == ".pdf" else "text/markdown"


def _sha256_bytes(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def _canonical_sha256(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return _sha256_bytes(encoded)


def _corpus_sha256(records: list[DownloadedSource]) -> str:
    rows = [{"source": record.source, "sha256": record.sha256} for record in records]
    return _canonical_sha256(sorted(rows, key=lambda row: row["source"]))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_name(f"{path.name}.part")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def _html_to_markdown(html: str, row: dict[str, Any]) -> str:
    parser = _VisibleTextParser()
    parser.feed(html)
    title = str(row.get("title", row["source"]))
    metadata_lines = [
        f"title: {title}",
        f"document_id: {row.get('document_id', Path(str(row['source'])).stem)}",
        f"jurisdiction: {row.get('jurisdiction', 'singapore')}",
        f"code_year: {row.get('code_year', '')}",
        f"document_version: {row.get('document_version', '')}",
        f"superseded: {str(row.get('superseded', False)).lower()}",
        f"source_type: {row.get('source_type', 'html')}",
        f"allowed_use: {row.get('allowed_use', '')}",
        f"publisher: {row.get('publisher', '')}",
        f"source_url: {row.get('source_url', '')}",
        f"rights: {row.get('rights', '')}",
        f"source_note: {row.get('source_note', '')}",
    ]
    return (
        "\n".join(metadata_lines)
        + "\n\n"
        + f"# {title}\n\n"
        + "Official public page converted to text for local retrieval review. "
        + "Verify against the source URL before relying on the content.\n\n"
        + parser.text()
        + "\n"
    )
