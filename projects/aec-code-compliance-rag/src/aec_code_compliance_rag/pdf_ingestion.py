from __future__ import annotations

from pathlib import Path

from .chunking import DocumentChunk, chunk_pdf_pages


def _read_pdf_pages(path: Path) -> list[tuple[int, str]]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - exercised only in missing-dep envs
        raise RuntimeError(
            "PDF ingestion requires pypdf. Install project requirements with "
            "`python -m pip install -r requirements.txt`."
        ) from exc

    reader = PdfReader(str(path))
    pages: list[tuple[int, str]] = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append((page_number, text))
    return pages


def load_pdf_chunks(
    path: str | Path,
    *,
    max_words: int = 110,
    metadata_overrides: dict[str, object] | None = None,
) -> list[DocumentChunk]:
    target = Path(path)
    return chunk_pdf_pages(
        _read_pdf_pages(target),
        source=target.name,
        max_words=max_words,
        metadata_overrides=metadata_overrides,
    )
