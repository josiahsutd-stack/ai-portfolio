from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DocumentChunk:
    text: str
    source: str
    section: str
    chunk_id: str


def _section_title(line: str, fallback: str) -> str:
    stripped = line.strip()
    if stripped.startswith("#"):
        return stripped.lstrip("#").strip() or fallback
    return fallback


def chunk_text(
    text: str, *, source: str, max_words: int = 110, overlap: int = 25
) -> list[DocumentChunk]:
    if not text.strip():
        return []
    words = text.split()
    chunks: list[DocumentChunk] = []
    section = Path(source).stem
    headings = [line for line in text.splitlines() if line.strip().startswith("#")]
    if headings:
        section = _section_title(headings[0], section)
    start = 0
    index = 0
    step = max(1, max_words - overlap)
    while start < len(words):
        end = min(start + max_words, len(words))
        chunk_words = words[start:end]
        if chunk_words:
            chunks.append(
                DocumentChunk(
                    text=" ".join(chunk_words),
                    source=source,
                    section=section,
                    chunk_id=f"{Path(source).stem}-{index:03d}",
                )
            )
        if end == len(words):
            break
        start += step
        index += 1
    return chunks


def load_markdown_chunks(path: str | Path, *, max_words: int = 110) -> list[DocumentChunk]:
    target = Path(path)
    return chunk_text(target.read_text(encoding="utf-8"), source=target.name, max_words=max_words)
