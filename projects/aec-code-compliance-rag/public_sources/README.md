# Public Source Corpus

This directory contains metadata for an optional Singapore public-document corpus.

Run:

```bash
python projects/aec-code-compliance-rag/scripts/download_public_sources.py
```

Downloaded PDFs and the generated `source_manifest.json` are written under `downloaded/`, which is ignored by Git. The committed `sources.json` file records source provenance and allowed-use notes.

The downloader is fail-closed for the supported source types:

- `.pdf` targets must contain a PDF signature; HTML error pages are rejected.
- HTML targets are converted to local Markdown only after content validation.
- Partial downloads produce `is_complete: false`, and unlisted stale files are excluded from retrieval.
- Accepted files record resolved URL, content type, byte count, and SHA-256.
- The manifest records deterministic source-inventory and corpus fingerprints.

The source inventory was manually checked against official landing pages on 18 July 2026. URLs and documents can still change; rerun the downloader and inspect `download_report.json` before each new evaluation snapshot.
