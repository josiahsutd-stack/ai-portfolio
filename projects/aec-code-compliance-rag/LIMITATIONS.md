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
- API authentication is one shared static key; there is no user identity, OAuth, RBAC, key rotation, or managed secret store.
- The local service has no TLS termination, reverse-proxy configuration, rate limiting, distributed tracing, multi-worker coordination, or durable metrics backend.
- Service metrics are process-local and reset on restart. The SQLite query log is a single-process review aid, not production telemetry.
- Question and response payloads are redacted by default, but this implementation choice is not a privacy, data-retention, or regulatory-compliance program.
- The service contract is evaluated in process. There is no external deployment, user traffic, load test, chaos test, penetration test, availability record, or incident-response evidence.
- Outputs are not legal, code, engineering, architectural, or professional compliance advice.
- Production use would require verified source authority, amendment/version monitoring, expert review, conflict resolution, security review, operational monitoring, and liability boundaries.
