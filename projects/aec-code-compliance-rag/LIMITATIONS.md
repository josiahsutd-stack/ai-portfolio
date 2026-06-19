# Limitations

- Synthetic AEC documents only.
- No live building codes, amendments, jurisdictions, or legal sources.
- Source manifest fields are synthetic review metadata, not verified legal source authority.
- PDF ingestion is limited to text-based PDFs; scanned documents, OCR, table reconstruction, and layout reasoning are not implemented.
- TF-IDF, BM25, dense LSA, and hybrid retrieval are portable local baselines, not hosted embedding or neural reranking systems.
- Citation faithfulness is a deterministic lexical coverage check, not full factual verification.
- Outputs are not legal, code, engineering, architectural, or professional compliance advice.
- Production use would require permissioned/public source documents, expert review, versioning, monitoring, and liability boundaries.
