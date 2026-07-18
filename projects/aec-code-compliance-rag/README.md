# AEC Code Compliance RAG Assistant

Primary review project for this AI engineering portfolio.

This is a local, source-grounded retrieval assistant for AEC guidance. The implemented workflow covers document chunking, source manifests, metadata-filtered retrieval, citation formatting, abstention, retrieval evaluation, and an authenticated local service contract with bounded durable telemetry.

The default corpus is synthetic demo data so the project runs without private data. An optional Singapore public-source workflow downloads official public BCA, URA, NEA, SCDF, LTA, PUB, and NParks documents locally for retrieval evaluation. Outputs are not legal, code, engineering, architectural, or professional compliance advice.

## Problem

Architecture, engineering, and construction teams often need to search across code clauses, planning notes, accessibility guidance, drawing QA standards, and internal assumptions before issuing work. A generic chatbot is risky in that setting because it can answer confidently without showing where the evidence came from.

This project focuses on a safer applied AI pattern: retrieve evidence first, show citations, expose retrieval metadata, and clearly state when the local demo corpus has no answer.

Design writeup: [Designing A Source-Grounded AEC RAG Assistant](../../docs/AEC_RAG_DESIGN_WRITEUP.md).

## Why It Matters

The project connects AI engineering with the built environment through inspectable retrieval, provenance, failure handling, and local service contracts. The evidence is bounded to the checked-in corpora, evaluations, and in-process workloads; it is not presented as a deployed compliance product.

Evidence in this repository:

- Evidence-first retrieval over synthetic AEC guidance and optional Singapore public-source documents.
- Singapore source inventory for BCA Accessibility, BCA Approved Document, BCA Green Mark, URA GFA, NEA COPEH, SCDF Fire Code, LTA interface codes, PUB drainage/sewerage codes, and NParks greenery/tree-conservation guidelines.
- Source manifest metadata for title, document type, allowed use, jurisdiction, version, and superseded status.
- Chunk metadata for section, heading, clause ID, PDF page or markdown page marker, chunk ID, and word offsets.
- Citation objects that include readable references, scores, excerpts, and traceable chunk IDs.
- Optional retrieval filters for jurisdiction, document type, and superseded-source handling.
- Source-status warnings for superseded, mixed-version, mixed-jurisdiction, or mixed-year evidence.
- Retrieval evaluation and mode ablation with sample questions and repeatable metrics.
- A fail-closed FastAPI service with API-key authentication, bounded request IDs, liveness/readiness checks, redacted SQLite query logs, process counters, and bounded payload-free request telemetry.
- Query-specific P95 latency and server-error objectives that remain `insufficient_data` until the configured sample size is reached.
- Tests for chunking, retrieval, citations, no-result handling, authentication, request tracing, log migration, redaction, telemetry retention/app-reconstruction behavior, objective states, and service errors.
- Clear architecture, limitations, demo artifacts, and production next steps.

## Quickstart

From the repository root:

```bash
python scripts/generate_sample_data.py
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py
python projects/aec-code-compliance-rag/evaluate_service.py
python projects/aec-code-compliance-rag/evaluate_service_reliability.py
pytest tests/test_rag.py tests/test_rag_service.py
streamlit run projects/aec-code-compliance-rag/app.py
```

The app runs locally without paid APIs. If `OPENAI_API_KEY` is not set, the assistant uses a deterministic local mock provider and still returns citation-bearing answers.

Optional Singapore public-source corpus:

```bash
python projects/aec-code-compliance-rag/scripts/download_public_sources.py
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py --corpus public
```

The downloaded PDFs/HTML text and generated manifest stay in `public_sources/downloaded/`, which is ignored by Git. The downloader fails on HTTP errors and PDF/content mismatches, then records resolved URLs, byte counts, file hashes, an inventory hash, and a corpus hash. The repository commits the source inventory, eval cases, and fingerprinted result artifacts, not redistributed government PDFs.

## Current Evidence Snapshot

| Evaluation | Scope | Hybrid result | Important boundary |
| --- | --- | --- | --- |
| Synthetic regression | 51 bundled cases | Recall@4 `1.000`; MRR `0.906`; Hit@3 `1.000` | Small authored corpus; useful for deterministic regression only. |
| Singapore public-source snapshot | 24 cases over 15 downloaded documents | Hit@1 `0.952`; MRR `0.976`; paraphrase MRR `0.917`; no-answer `1.000` | Documents were downloaded and validated on 18 July 2026; no authority or expert applicability review. |
| Local service contract | 12 in-process ASGI checks | 12/12 checks passed; 9 requests and 3 client errors observed before the metrics response | Synthetic corpus; no external deployment, traffic, load, availability, or security assessment. |
| Local reliability evaluation | 48 requests at maximum concurrency 8 | 48/48 responses returned 200; 0 server errors; P95 at or below 500 ms; 48 durable query rows survived app reconstruction | Warmed in-process ASGI workload on one local machine; not network, sustained-load, uptime, or capacity evidence. |

The public run includes 15 direct questions, six paraphrases, two project-specific no-evidence cases, and one professional-review refusal. Two paraphrase cases retrieve the correct source but miss one expected phrase within the top four chunks; those cases remain in [`failure_analysis.md`](demo_outputs/public_sources/failure_analysis.md).

## Demo

```bash
streamlit run projects/aec-code-compliance-rag/app.py
```

Deployment notes for Streamlit Community Cloud, Render, and Hugging Face Spaces are in [DEPLOYMENT.md](DEPLOYMENT.md).

![AEC RAG Streamlit demo](../../docs/assets/screenshots/aec-rag-demo.png)

Try these questions:

- What clear width should be checked for high traffic accessible routes?
- What doorway and threshold checks apply to accessible rooms?
- What should be included for long residential corridors?
- What daylight risks should west glazing trigger?
- Which assumptions should be logged before a planning submission?
- What should PDF extracted accessible parking notes record for wet-weather transfers?

Generated evaluation artifacts are in [`demo_outputs/`](demo_outputs/):

- [`retrieval_eval_summary.json`](demo_outputs/retrieval_eval_summary.json)
- [`evaluation_manifest.json`](demo_outputs/evaluation_manifest.json)
- [`retrieval_eval_report.md`](demo_outputs/retrieval_eval_report.md)
- [`retrieval_ablation_summary.json`](demo_outputs/retrieval_ablation_summary.json)
- [`retrieval_ablation_report.md`](demo_outputs/retrieval_ablation_report.md)
- [`accessible_route_answer.md`](demo_outputs/accessible_route_answer.md)
- [`no_answer_failure_case.md`](demo_outputs/no_answer_failure_case.md)
- [`service_contract_summary.json`](demo_outputs/service_contract_summary.json)
- [`service_contract_report.md`](demo_outputs/service_contract_report.md)
- [`service_reliability_summary.json`](demo_outputs/service_reliability_summary.json)
- [`service_reliability_report.md`](demo_outputs/service_reliability_report.md)
- [`public_sources/`](demo_outputs/public_sources/) for optional Singapore public-source eval outputs after running the public corpus command.

Regenerate them with:

```bash
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py
python projects/aec-code-compliance-rag/evaluate_service.py
python projects/aec-code-compliance-rag/evaluate_service_reliability.py
```

## Features

- Markdown and text-based PDF document ingestion from `sample_data/`.
- Optional Singapore public-source downloader for BCA, URA, NEA, SCDF, LTA, PUB, and NParks reference documents.
- Source manifest loading from `sample_data/source_manifest.json`.
- Fail-closed public-source download validation with resolved-URL and SHA-256 provenance.
- Section-aware chunking with overlap.
- Metadata fields for title, source type, allowed use, heading, clause ID, PDF page or markdown page marker, chunk ID, and word offsets.
- Per-query source filters for jurisdiction, authority/publisher, document family, source type, and superseded-source exclusion.
- Conservative authority/document inference so BCA, PUB, NParks, URA, NEA, SCDF, and LTA questions stay within the named agency or document family where possible.
- Local TF-IDF, BM25, dense LSA, and hybrid retrieval modes, with optional sentence-transformer embedding and cross-encoder reranking modes.
- Retrieval ablation report comparing modes over the same synthetic eval set.
- Deterministic no-API answer mode plus optional OpenAI-compatible provider through shared portfolio utilities.
- Citation formatting with references like `[C1] mock_aec_guidance.md > Accessible Routes`.
- Source-status analysis that flags retrieved evidence requiring version/jurisdiction review.
- Retrieval evaluation over sample questions.
- No-answer evaluation for unsupported compliance questions.
- Versioned demo-output generation.
- Streamlit public/synthetic corpus switch and an API-key-protected FastAPI review service.
- Public liveness/readiness checks plus authenticated source, query, retrieval, log, and metrics endpoints.
- Durable local route/status/latency rows with fixed retention, payload exclusion, app-reconstruction persistence, and fail-open write handling.
- Tests covering chunking, retrieval, citations, no-result handling, eval scoring, authentication, tracing, redaction, service failures, telemetry retention, app-reconstruction persistence, and objective transitions.

## Architecture And Evaluation Docs

- [`ARCHITECTURE.md`](ARCHITECTURE.md) explains the data flow, module boundaries, metadata contract, and production extension points.
- [`EVAL.md`](EVAL.md) explains the evaluation dataset, metrics, known failure modes, and how to interpret the sample results.
- [`DEPLOYMENT.md`](DEPLOYMENT.md) documents the verified local service boundary and clearly separates unverified hosting options.
- [`LIMITATIONS.md`](LIMITATIONS.md), [`CASE_STUDY.md`](CASE_STUDY.md), and [`SYSTEM_CARD.md`](SYSTEM_CARD.md) define project boundaries and review context.

## How It Works

1. Synthetic markdown guidance, a generated PDF addendum, and `source_manifest.json` are loaded from `sample_data/`; alternatively, the public-source workflow loads downloaded Singapore official documents plus a generated source manifest.
2. Markdown files are split by headings and optional page markers such as `<!-- page: 2 -->`; PDFs are extracted page by page with `pypdf`.
3. Manifest records override or enrich document metadata before chunks are indexed.
4. Each chunk receives traceable metadata: source, title, source type, allowed use, section, heading, clause ID, page value, chunk ID, start word, end word, document version, jurisdiction, code year, and superseded status.
5. A local retriever ranks the eligible source subset for a question. The default app mode is hybrid TF-IDF/BM25; the eval script also compares TF-IDF, BM25, dense LSA, and hybrid modes.
6. The assistant returns an answer only from retrieved evidence, exposes structured citations, and warns when retrieved sources need version or jurisdiction review.
7. The retrieval evaluator runs sample questions and writes metrics plus demo outputs.
8. The service factory applies API-key authentication, request IDs, readiness checks, redacted query logs, process counters, and bounded payload-free SQLite telemetry around the same assistant boundary.
9. Query objectives evaluate the latest durable `POST /query` window only after a minimum sample count; the fixed workload reconstructs the app to verify persistence.

## Tests

```bash
pytest tests/test_rag.py tests/test_rag_service.py
```

The tests cover:

- Chunk metadata and page-marker parsing.
- Retrieval of the expected section.
- Dense LSA retrieval metadata and retrieval-mode ablation.
- Citation formatting and chunk IDs.
- Document-version, jurisdiction, and superseded-source metadata.
- Source manifest overrides and filtered retrieval behavior.
- Empty and no-result handling.
- Project-specific questions that lack project records.
- Retrieval evaluation metrics.
- Fail-closed authentication and readiness behavior.
- Request-ID propagation and sanitization.
- Default query-payload redaction, explicit payload opt-in, and legacy SQLite schema migration.
- Success and failure audit records plus process and durable route/status/latency metrics.
- Bounded telemetry retention, payload-field exclusion, fail-open write handling, app-reconstruction persistence, and insufficient/pass/fail objective states.

## Optional Public-Source Review

The public corpus tests the same retrieval pipeline against downloaded official documents while keeping redistribution boundaries clean. It includes source metadata for:

- BCA Code on Accessibility in the Built Environment 2025.
- BCA Approved Document and Green Mark 2021 documents.
- URA Gross Floor Area handbook and GFA guidelines-at-a-glance.
- NEA Code of Practice on Environmental Health 2025.
- SCDF Fire Code 2023.
- LTA works on public streets and railway protection codes.
- PUB codes of practice for surface water drainage, sewerage/sanitary works, and coastal-protection listing.
- NParks greenery provision, tree conservation, and development-plan submission references.

Run `python projects/aec-code-compliance-rag/scripts/download_public_sources.py` before `--corpus public`. The app then exposes a `Singapore public sources` corpus option.

## API Review

PowerShell from the repository root:

```powershell
$env:AEC_RAG_API_KEY = "local-review-key"
python -m uvicorn api:app --app-dir projects/aec-code-compliance-rag --host 127.0.0.1 --port 8000
```

`/health/live` and `/health/ready` are public. `/sources`, `/query`, `/retrieve`, `/logs/recent`, and `/metrics` require the key in the `X-API-Key` header. Query text and response payloads are redacted in the local SQLite log unless `AEC_RAG_LOG_PAYLOADS=true` is explicitly configured.

Reproduce the checked-in service evidence without starting a network listener:

```bash
python projects/aec-code-compliance-rag/evaluate_service.py
python projects/aec-code-compliance-rag/evaluate_service_reliability.py
```

The first evaluator checks interface behavior. The second warms the index, sends 48 queries with maximum concurrency 8, checks a 500 ms P95 and 0.01 server-error-rate budget, then reconstructs the app against the same SQLite file. Both are in-process and synthetic; neither is deployment, sustained-load, uptime, or usage evidence.

## Limitations

- The default corpus is synthetic and intentionally small.
- The optional Singapore public corpus downloads official public documents locally, but it is still not a validated compliance engine.
- PDF ingestion is text-based and page-aware, but it does not handle scanned PDFs, OCR, table reconstruction, or layout geometry.
- TF-IDF, BM25, dense LSA, and hybrid modes are transparent and local. Optional embedding/reranking modes require `requirements-embeddings.txt` and model downloads.
- The local answer mode is deterministic and extractive; it is not a real expert model.
- API authentication is one static shared key. There is no user identity, OAuth, RBAC, rate limiting, TLS termination, or secret manager.
- Process counters reset on restart. Bounded route/status/latency rows and redacted query logs persist in one local SQLite file, which is not a distributed metrics backend.
- The service has not been externally deployed, network load tested, penetration tested, or observed under user traffic. The fixed concurrent ASGI workload does not establish capacity or availability.
- The project does not certify against current building-code amendments, authority interpretations, project submissions, or professional review requirements.
- No real project, client, or construction data is included.

## Next Steps

- Improve PDF ingestion with layout-aware table extraction, OCR fallback, and clause-level parsing.
- Improve Singapore source refresh checks, amendment detection, and source inventory validation.
- Benchmark optional embedding and cross-encoder retrieval against the public-source eval set.
- Strengthen citation-faithfulness checks beyond the current deterministic lexical coverage check.
- Expand the public evaluation with expert-labeled clause and page targets, ambiguous jurisdiction cases, and adversarial wording.
- Add stronger conflict detection for contradictory source content and superseded clauses.
- Add an expert-review queue for uncertain answers.
- Add identity-aware authorization, rate limits, managed secrets, distributed telemetry, reverse-proxy/network load tests, and deployment checks before considering an externally reachable service.

## Evidence

- Practical RAG system design for a domain workflow.
- Source-grounded answer design and citation ergonomics.
- Retrieval evaluation and failure analysis discipline.
- Local-first execution without paid APIs.
- Honest separation between demo behavior and production compliance requirements.

## Implementation Notes

- The system uses deterministic chunk IDs and metadata so retrieval results can be inspected and tested.
- `source_manifest.json` makes document status explicit instead of relying only on file headers.
- Markdown page markers and extracted PDF page numbers use the same citation metadata contract.
- The assistant refuses empty questions and returns a no-evidence response when retrieval has no matching chunks.
- The included retrieval modes are portable baselines, not final retrieval choices for a real compliance product.

## Design Decisions

- How should retrieval be evaluated before an AEC assistant is trusted by practitioners?
- What metadata is required for citations to be auditable?
- Where should expert review sit in a compliance workflow?
- How would embedding retrieval, reranking, and stronger citation-faithfulness checks change the architecture?
- Which claims can this demo support, and which claims would require real data, legal review, and production monitoring?
