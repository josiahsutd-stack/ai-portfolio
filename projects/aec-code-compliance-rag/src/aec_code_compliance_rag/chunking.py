from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

DOCUMENT_METADATA_FIELDS = {
    "document_id",
    "jurisdiction",
    "code_year",
    "document_version",
    "superseded",
    "title",
    "source_type",
    "allowed_use",
}


@dataclass(frozen=True)
class DocumentChunk:
    text: str
    source: str
    section: str
    heading: str
    clause_id: str
    page: int | None
    chunk_id: str
    start_word: int
    end_word: int
    document_id: str = "synthetic-demo"
    jurisdiction: str = "synthetic-demo"
    code_year: str = "synthetic"
    document_version: str = "demo"
    superseded: bool = False
    title: str = ""
    source_type: str = "document"
    allowed_use: str = "synthetic_demo"

    def metadata(self) -> dict[str, str]:
        return {
            "source": self.source,
            "title": self.title,
            "source_type": self.source_type,
            "allowed_use": self.allowed_use,
            "document_id": self.document_id,
            "section": self.section,
            "heading": self.heading,
            "clause_id": self.clause_id,
            "page": "" if self.page is None else str(self.page),
            "chunk_id": self.chunk_id,
            "start_word": str(self.start_word),
            "end_word": str(self.end_word),
            "jurisdiction": self.jurisdiction,
            "code_year": self.code_year,
            "document_version": self.document_version,
            "superseded": str(self.superseded).lower(),
        }


def _section_title(line: str, fallback: str) -> str:
    stripped = line.strip()
    if stripped.startswith("#"):
        return stripped.lstrip("#").strip() or fallback
    return fallback


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "section"


def _metadata_key(raw_key: str) -> str:
    return raw_key.strip().lower().replace(" ", "_").replace("-", "_")


def _metadata_value(key: str, value: object) -> str:
    if key == "superseded" and isinstance(value, bool):
        return str(value).lower()
    return str(value).strip()


def _merge_document_metadata(
    base: dict[str, str], overrides: dict[str, object] | None
) -> dict[str, str]:
    merged = dict(base)
    for raw_key, raw_value in (overrides or {}).items():
        key = _metadata_key(str(raw_key))
        if key in DOCUMENT_METADATA_FIELDS and raw_value is not None:
            merged[key] = _metadata_value(key, raw_value)
    return merged


def _is_document_metadata_line(line: str) -> bool:
    match = re.match(r"\s*([a-zA-Z_ -]+):\s*(.+?)\s*$", line)
    return bool(match and _metadata_key(match.group(1)) in DOCUMENT_METADATA_FIELDS)


def _iter_markdown_sections(text: str, *, source: str) -> list[tuple[str, str, int | None, str]]:
    """Return `(section, heading, page, body)` sections from a markdown document.

    Markdown page values come from optional HTML-style comments such as
    `<!-- page: 2 -->`; otherwise the page is kept as `None`.
    """

    fallback = Path(source).stem
    current_section = fallback
    current_heading = fallback
    current_page: int | None = None
    current_lines: list[str] = []
    sections: list[tuple[str, str, int | None, str]] = []

    def flush() -> None:
        body = "\n".join(current_lines).strip()
        if body:
            sections.append((current_section, current_heading, current_page, body))

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        page_match = re.search(r"<!--\s*page:\s*(\d+)\s*-->", line, flags=re.IGNORECASE)
        if page_match:
            flush()
            current_lines = []
            current_page = int(page_match.group(1))
            continue
        if line.strip().startswith("#"):
            flush()
            current_lines = []
            current_heading = _section_title(line, fallback)
            current_section = current_heading
            continue
        current_lines.append(line)
    flush()
    if not sections and text.strip():
        return [(fallback, fallback, current_page, text.strip())]
    return sections


def _chunks_from_sections(
    sections: list[tuple[str, str, int | None, str]],
    *,
    source: str,
    metadata: dict[str, str],
    max_words: int = 110,
    overlap: int = 25,
    include_page_in_chunk_id: bool = False,
) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    step = max(1, max_words - overlap)
    for section, heading, page, body in sections:
        words = body.split()
        if not words:
            continue
        start = 0
        index = 0
        while start < len(words):
            end = min(start + max_words, len(words))
            chunk_words = words[start:end]
            if chunk_words:
                clause_id = f"AEC-{_slug(heading).upper()}"
                page_part = f"-p{page}" if include_page_in_chunk_id and page is not None else ""
                chunk_id = f"{Path(source).stem}-{_slug(heading)}{page_part}-{index:03d}"
                chunks.append(
                    DocumentChunk(
                        text=f"{heading}. {' '.join(chunk_words)}",
                        source=source,
                        section=section,
                        heading=heading,
                        clause_id=clause_id,
                        page=page,
                        chunk_id=chunk_id,
                        start_word=start,
                        end_word=end,
                        document_id=metadata["document_id"],
                        jurisdiction=metadata["jurisdiction"],
                        code_year=metadata["code_year"],
                        document_version=metadata["document_version"],
                        superseded=metadata["superseded"].lower() == "true",
                        title=metadata["title"],
                        source_type=metadata["source_type"],
                        allowed_use=metadata["allowed_use"],
                    )
                )
            if end == len(words):
                break
            start += step
            index += 1
    return chunks


def chunk_text(
    text: str,
    *,
    source: str,
    max_words: int = 110,
    overlap: int = 25,
    metadata_overrides: dict[str, object] | None = None,
) -> list[DocumentChunk]:
    if not text.strip():
        return []
    metadata = _merge_document_metadata(
        _extract_document_metadata(text, source=source),
        metadata_overrides,
    )
    return _chunks_from_sections(
        _iter_markdown_sections(text, source=source),
        source=source,
        metadata=metadata,
        max_words=max_words,
        overlap=overlap,
    )


def _split_pdf_page_heading_and_body(lines: list[str], *, fallback: str) -> tuple[str, str]:
    for index, raw_line in enumerate(lines):
        stripped = raw_line.strip()
        if stripped:
            heading = stripped.lstrip("#").strip() or fallback
            body = "\n".join(lines[index + 1 :]).strip() or heading
            return heading, body
    return fallback, ""


def chunk_pdf_pages(
    pages: list[tuple[int, str]],
    *,
    source: str,
    max_words: int = 110,
    overlap: int = 25,
    metadata_overrides: dict[str, object] | None = None,
) -> list[DocumentChunk]:
    page_texts = [(page_number, text) for page_number, text in pages if text.strip()]
    if not page_texts:
        return []
    combined_text = "\n".join(text for _page_number, text in page_texts)
    metadata = _merge_document_metadata(
        _extract_document_metadata(combined_text, source=source),
        metadata_overrides,
    )
    fallback = Path(source).stem
    sections: list[tuple[str, str, int | None, str]] = []
    for page_number, page_text in page_texts:
        content_lines = [
            line for line in page_text.splitlines() if not _is_document_metadata_line(line)
        ]
        heading, body = _split_pdf_page_heading_and_body(
            content_lines,
            fallback=f"{fallback} page {page_number}",
        )
        if body:
            sections.append((heading, heading, page_number, body))
    return _chunks_from_sections(
        sections,
        source=source,
        metadata=metadata,
        max_words=max_words,
        overlap=overlap,
        include_page_in_chunk_id=True,
    )


def _extract_document_metadata(text: str, *, source: str) -> dict[str, str]:
    suffix = Path(source).suffix.lower()
    source_type = (
        "pdf" if suffix == ".pdf" else "markdown" if suffix in {".md", ".markdown"} else "document"
    )
    metadata = {
        "document_id": Path(source).stem,
        "jurisdiction": "synthetic-demo",
        "code_year": "synthetic",
        "document_version": "demo",
        "superseded": "false",
        "title": Path(source).stem.replace("_", " ").replace("-", " ").title(),
        "source_type": source_type,
        "allowed_use": "synthetic_demo",
    }
    for line in text.splitlines()[:40]:
        match = re.match(r"\s*([a-zA-Z_ -]+):\s*(.+?)\s*$", line)
        if not match:
            continue
        key = _metadata_key(match.group(1))
        value = match.group(2).strip()
        if key in metadata:
            metadata[key] = value
    return metadata


def load_markdown_chunks(
    path: str | Path,
    *,
    max_words: int = 110,
    metadata_overrides: dict[str, object] | None = None,
) -> list[DocumentChunk]:
    target = Path(path)
    return chunk_text(
        target.read_text(encoding="utf-8"),
        source=target.name,
        max_words=max_words,
        metadata_overrides=metadata_overrides,
    )


def load_document_chunks(
    path: str | Path,
    *,
    max_words: int = 110,
    metadata_overrides: dict[str, object] | None = None,
) -> list[DocumentChunk]:
    target = Path(path)
    suffix = target.suffix.lower()
    if suffix in {".md", ".markdown"}:
        return load_markdown_chunks(
            target,
            max_words=max_words,
            metadata_overrides=metadata_overrides,
        )
    if suffix == ".pdf":
        from .pdf_ingestion import load_pdf_chunks

        return load_pdf_chunks(
            target,
            max_words=max_words,
            metadata_overrides=metadata_overrides,
        )
    raise ValueError(f"Unsupported AEC document type: {target.suffix or target.name}")
