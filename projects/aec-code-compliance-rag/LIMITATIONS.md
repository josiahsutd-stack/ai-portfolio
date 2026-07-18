# Limitations

- Synthetic AEC documents by default.
- Optional Singapore public-source documents can be downloaded locally for BCA, URA, NEA, SCDF, LTA, PUB, and NParks retrieval tests, but the PDFs/HTML snapshots are not committed to Git.
- The committed public metrics describe one fingerprinted 18 July 2026 download snapshot. Source URLs, amendments, and document contents can change after that run.
- The 24 public evaluation cases are authored for this project and have not been independently labeled by code consultants or regulatory authorities.
- No authority approval, legal interpretation, amendment monitoring, project-specific applicability check, or professional sign-off is provided.
- Source manifest fields are review metadata, not verified legal source authority.
- PDF ingestion is limited to text-based PDFs; scanned documents, OCR, table reconstruction, and layout reasoning are not implemented.
- TF-IDF, BM25, dense LSA, and hybrid retrieval are portable local baselines. Optional embedding and cross-encoder modes require additional model dependencies.
- Citation faithfulness is a deterministic lexical coverage check, not full factual verification.
- Project-specific markers trigger abstention when project records are absent; this is a conservative rule boundary, not learned applicability reasoning.
- Outputs are not legal, code, engineering, architectural, or professional compliance advice.
- Production use would require verified source authority, amendment/version monitoring, expert review, conflict resolution, security review, operational monitoring, and liability boundaries.
