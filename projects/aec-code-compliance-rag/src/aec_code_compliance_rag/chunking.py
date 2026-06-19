from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


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

    def metadata(self) -> dict[str, str]:
        return {
            "source": self.source,
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


def _iter_markdown_sections(text: str, *, source: str) -> list[tuple[str, str, int | None, str]]:
    """Return `(section, heading, page, body)` sections from a markdown document.

    The demo documents are markdown, not PDFs. `page` is therefore inferred only
    from optional HTML-style comments such as `<!-- page: 2 -->`; otherwise it is
    kept as `None` rather than pretending a real PDF page exists.
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


def chunk_text(
    text: str, *, source: str, max_words: int = 110, overlap: int = 25
) -> list[DocumentChunk]:
    if not text.strip():
        return []
    chunks: list[DocumentChunk] = []
    metadata = _extract_document_metadata(text, source=source)
    step = max(1, max_words - overlap)
    for section, heading, page, body in _iter_markdown_sections(text, source=source):
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
                chunk_id = f"{Path(source).stem}-{_slug(heading)}-{index:03d}"
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
                    )
                )
            if end == len(words):
                break
            start += step
            index += 1
    return chunks


def _extract_document_metadata(text: str, *, source: str) -> dict[str, str]:
    metadata = {
        "document_id": Path(source).stem,
        "jurisdiction": "synthetic-demo",
        "code_year": "synthetic",
        "document_version": "demo",
        "superseded": "false",
    }
    for line in text.splitlines()[:40]:
        match = re.match(r"\s*([a-zA-Z_ -]+):\s*(.+?)\s*$", line)
        if not match:
            continue
        key = match.group(1).strip().lower().replace(" ", "_").replace("-", "_")
        value = match.group(2).strip()
        if key in metadata:
            metadata[key] = value
    return metadata


def load_markdown_chunks(path: str | Path, *, max_words: int = 110) -> list[DocumentChunk]:
    target = Path(path)
    return chunk_text(target.read_text(encoding="utf-8"), source=target.name, max_words=max_words)
