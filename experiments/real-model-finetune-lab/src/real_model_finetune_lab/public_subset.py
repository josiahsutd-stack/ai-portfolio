from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import unicodedata
import urllib.request
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

SOURCE_ARCHIVE_URL = "https://archive.ics.uci.edu/static/public/228/sms%2Bspam%2Bcollection.zip"
SOURCE_ARCHIVE_SHA256 = "1587ea43e58e82b14ff1f5425c88e17f8496bfcdb67a583dbff9eefaf9963ce3"
SOURCE_MEMBER = "SMSSpamCollection"
SELECTION_SEED = "ai-portfolio-public-sms-v1"
ROWS_PER_LABEL = 120
SPLIT_COUNTS = {"train": 80, "validation": 20, "test": 20}
LABELS = ("ham", "spam")


@dataclass(frozen=True)
class SourceMessage:
    source_row: int
    label: str
    text: str


@dataclass(frozen=True)
class SubsetMessage:
    source_row: int
    split: str
    label: str
    text: str


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def normalize_text(text: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", ascii_text).strip()


def parse_source_text(source_text: str) -> list[SourceMessage]:
    messages: list[SourceMessage] = []
    for source_row, line in enumerate(source_text.splitlines(), start=1):
        if "\t" not in line:
            raise ValueError(f"source row {source_row} has no tab-separated label")
        label, text = line.split("\t", 1)
        if label not in LABELS:
            raise ValueError(f"source row {source_row} has unsupported label `{label}`")
        normalized = normalize_text(text)
        if not normalized:
            raise ValueError(f"source row {source_row} is empty after normalization")
        messages.append(SourceMessage(source_row=source_row, label=label, text=normalized))
    return messages


def load_source_archive(path: str | Path) -> list[SourceMessage]:
    archive = Path(path)
    payload = archive.read_bytes()
    actual_hash = sha256_bytes(payload)
    if actual_hash != SOURCE_ARCHIVE_SHA256:
        raise ValueError(
            f"source archive SHA-256 mismatch: expected {SOURCE_ARCHIVE_SHA256}, got {actual_hash}"
        )
    with zipfile.ZipFile(io.BytesIO(payload)) as source_zip:
        try:
            source_text = source_zip.read(SOURCE_MEMBER).decode("utf-8")
        except KeyError as exc:
            raise ValueError(f"source archive is missing `{SOURCE_MEMBER}`") from exc
    return parse_source_text(source_text)


def download_source_archive(path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(SOURCE_ARCHIVE_URL, timeout=30) as response:  # noqa: S310
        payload = response.read()
    actual_hash = sha256_bytes(payload)
    if actual_hash != SOURCE_ARCHIVE_SHA256:
        raise ValueError(
            f"downloaded archive SHA-256 mismatch: expected {SOURCE_ARCHIVE_SHA256}, got {actual_hash}"
        )
    target.write_bytes(payload)
    return target


def _rank(message: SourceMessage, purpose: str) -> str:
    payload = (
        f"{purpose}|{SELECTION_SEED}|{message.source_row}|{message.label}|{message.text}"
    ).encode()
    return sha256_bytes(payload)


def build_subset(messages: list[SourceMessage]) -> list[SubsetMessage]:
    unique_by_text: dict[str, SourceMessage] = {}
    for message in messages:
        existing = unique_by_text.get(message.text)
        if existing is None or message.source_row < existing.source_row:
            unique_by_text[message.text] = message

    by_label: dict[str, list[SourceMessage]] = defaultdict(list)
    for message in unique_by_text.values():
        by_label[message.label].append(message)

    selected: list[SubsetMessage] = []
    for label in LABELS:
        candidates = sorted(by_label[label], key=lambda row: _rank(row, "select"))
        if len(candidates) < ROWS_PER_LABEL:
            raise ValueError(f"label `{label}` has only {len(candidates)} unique candidates")
        label_rows = sorted(candidates[:ROWS_PER_LABEL], key=lambda row: _rank(row, "split"))
        start = 0
        for split, count in SPLIT_COUNTS.items():
            for message in label_rows[start : start + count]:
                selected.append(
                    SubsetMessage(
                        source_row=message.source_row,
                        split=split,
                        label=message.label,
                        text=message.text,
                    )
                )
            start += count
    return sorted(
        selected,
        key=lambda row: _rank(
            SourceMessage(source_row=row.source_row, label=row.label, text=row.text), "order"
        ),
    )


def subset_tsv(rows: list[SubsetMessage]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        buffer,
        fieldnames=["source_row", "split", "label", "text"],
        delimiter="\t",
        lineterminator="\n",
    )
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {
                "source_row": row.source_row,
                "split": row.split,
                "label": row.label,
                "text": row.text,
            }
        )
    return buffer.getvalue()


def subset_manifest(rows: list[SubsetMessage], tsv_payload: bytes) -> dict[str, object]:
    split_counts: dict[str, dict[str, int]] = {}
    for split in SPLIT_COUNTS:
        counts = Counter(row.label for row in rows if row.split == split)
        split_counts[split] = {label: counts[label] for label in LABELS}
    return {
        "source": {
            "name": "UCI SMS Spam Collection",
            "url": "https://archive.ics.uci.edu/dataset/228/sms%2Bspam%2Bcollection",
            "doi": "10.24432/C5CC84",
            "license": "CC BY 4.0",
            "archive_url": SOURCE_ARCHIVE_URL,
            "archive_sha256": SOURCE_ARCHIVE_SHA256,
            "member": SOURCE_MEMBER,
            "source_row_numbering": "one-based line number in SMSSpamCollection",
        },
        "selection": {
            "version": "sha256-ranked-balanced-v1",
            "seed": SELECTION_SEED,
            "normalization": "NFKD to ASCII, then collapse whitespace",
            "deduplication": "retain first source row for each normalized text before selection",
            "ranking": "SHA-256 rank for selection, split assignment, and output order",
            "rows_per_label": ROWS_PER_LABEL,
            "split_rows_per_label": SPLIT_COUNTS,
        },
        "output": {
            "row_count": len(rows),
            "split_label_counts": split_counts,
            "tsv_sha256": sha256_bytes(tsv_payload),
        },
    }


def write_subset(
    rows: list[SubsetMessage], tsv_path: str | Path, manifest_path: str | Path
) -> None:
    tsv_target = Path(tsv_path)
    manifest_target = Path(manifest_path)
    tsv_target.parent.mkdir(parents=True, exist_ok=True)
    payload = subset_tsv(rows).encode("utf-8")
    tsv_target.write_bytes(payload)
    manifest_target.write_text(
        json.dumps(subset_manifest(rows, payload), indent=2) + "\n", encoding="utf-8"
    )


def validate_checked_in_subset(tsv_path: str | Path, manifest_path: str | Path) -> list[str]:
    tsv_target = Path(tsv_path)
    manifest_target = Path(manifest_path)
    if not tsv_target.exists():
        return [f"missing subset TSV: {tsv_target}"]
    if not manifest_target.exists():
        return [f"missing subset manifest: {manifest_target}"]
    try:
        manifest = json.loads(manifest_target.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid subset manifest JSON: {exc}"]

    payload = tsv_target.read_bytes()
    issues: list[str] = []
    source = manifest.get("source")
    selection = manifest.get("selection")
    output = manifest.get("output")
    if (
        not isinstance(source, dict)
        or not isinstance(selection, dict)
        or not isinstance(output, dict)
    ):
        return ["subset manifest must contain source, selection, and output mappings"]
    if source.get("archive_sha256") != SOURCE_ARCHIVE_SHA256:
        issues.append("subset manifest source archive hash does not match the pinned hash")
    expected_selection = {
        "version": "sha256-ranked-balanced-v1",
        "seed": SELECTION_SEED,
        "rows_per_label": ROWS_PER_LABEL,
        "split_rows_per_label": SPLIT_COUNTS,
    }
    for key, expected_value in expected_selection.items():
        if selection.get(key) != expected_value:
            issues.append(
                f"subset manifest selection `{key}` differs: "
                f"expected {expected_value}, got {selection.get(key)}"
            )

    expected_hash = output.get("tsv_sha256")
    actual_hash = sha256_bytes(payload)
    if actual_hash != expected_hash:
        issues.append(f"subset TSV hash mismatch: expected {expected_hash}, got {actual_hash}")

    try:
        rows = list(csv.DictReader(io.StringIO(payload.decode("utf-8")), delimiter="\t"))
    except UnicodeDecodeError as exc:
        return [*issues, f"subset TSV is not UTF-8: {exc}"]
    required = {"source_row", "split", "label", "text"}
    if not rows or set(rows[0]) != required:
        issues.append(f"subset TSV columns must be {sorted(required)}")
        return issues
    if len({row["source_row"] for row in rows}) != len(rows):
        issues.append("subset TSV contains duplicate source rows")
    if len({row["text"] for row in rows}) != len(rows):
        issues.append("subset TSV contains duplicate normalized messages")
    if any(not row["source_row"].isdigit() or int(row["source_row"]) < 1 for row in rows):
        issues.append("subset TSV contains an invalid one-based source row")
    if any(row["text"] != normalize_text(row["text"]) for row in rows):
        issues.append("subset TSV contains text outside the documented normalization")

    actual_counts: dict[str, dict[str, int]] = {}
    for split in SPLIT_COUNTS:
        counts = Counter(row["label"] for row in rows if row["split"] == split)
        actual_counts[split] = {label: counts[label] for label in LABELS}
    expected_counts = output.get("split_label_counts")
    if actual_counts != expected_counts:
        issues.append(
            f"subset split counts differ: expected {expected_counts}, got {actual_counts}"
        )
    if any(row["split"] not in SPLIT_COUNTS for row in rows):
        issues.append("subset TSV contains an unsupported split")
    if any(row["label"] not in LABELS for row in rows):
        issues.append("subset TSV contains an unsupported label")
    if output.get("row_count") != len(rows):
        issues.append(
            f"subset row count differs: expected {output.get('row_count')}, got {len(rows)}"
        )
    return issues
