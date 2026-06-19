# Limitations

- Synthetic AEC documents by default.
- Optional Singapore public-source documents can be downloaded locally for BCA, URA, NEA, SCDF, LTA, PUB, and NParks retrieval tests, but the PDFs/HTML snapshots are not committed to Git.
- No authority approval, legal interpretation, amendment monitoring, project-specific applicability check, or professional sign-off is provided.
- Source manifest fields are review metadata, not verified legal source authority.
- PDF ingestion is limited to text-based PDFs; scanned documents, OCR, table reconstruction, and layout reasoning are not implemented.
- TF-IDF, BM25, dense LSA, and hybrid retrieval are portable local baselines. Optional embedding and cross-encoder modes require additional model dependencies.
- Citation faithfulness is a deterministic lexical coverage check, not full factual verification.
- Outputs are not legal, code, engineering, architectural, or professional compliance advice.
- Production use would require verified source authority, amendment/version monitoring, expert review, conflict resolution, security review, operational monitoring, and liability boundaries.
