# AEC Code Compliance RAG Assistant

Primary review project for this AI engineering portfolio.

This is a local, source-grounded retrieval assistant for AEC guidance. It demonstrates the engineering shape behind a compliance-oriented RAG workflow: document chunking, source manifests, metadata-filtered retrieval, citation formatting, evaluation questions, demo outputs, and failure handling.

The default corpus is synthetic demo data so the project runs without private data. An optional Singapore public-source workflow downloads official public BCA, URA, NEA, SCDF, LTA, PUB, and NParks documents locally for retrieval evaluation. Outputs are not legal, code, engineering, architectural, or professional compliance advice.

## Problem

Architecture, engineering, and construction teams often need to search across code clauses, planning notes, accessibility guidance, drawing QA standards, and internal assumptions before issuing work. A generic chatbot is risky in that setting because it can answer confidently without showing where the evidence came from.

This project focuses on a safer applied AI pattern: retrieve evidence first, show citations, expose retrieval metadata, and clearly state when the local demo corpus has no answer.

Design writeup: [Designing A Source-Grounded AEC RAG Assistant](../../docs/AEC_RAG_DESIGN_WRITEUP.md).

## Why It Matters

The project connects AI engineering with the built environment. It shows how a junior/applied AI engineer can structure a domain RAG system without pretending the demo is a deployed compliance product.

Evidence in this repository:

- Evidence-first retrieval over synthetic AEC guidance and optional Singapore public-source documents.
- Singapore source inventory for BCA Accessibility, BCA Approved Document, BCA Green Mark, URA GFA, NEA COPEH, SCDF Fire Code, LTA interface codes, PUB drainage/sewerage codes, and NParks greenery/tree-conservation guidelines.
- Source manifest metadata for title, document type, allowed use, jurisdiction, version, and superseded status.
- Chunk metadata for section, heading, clause ID, PDF page or markdown page marker, chunk ID, and word offsets.
- Citation objects that include readable references, scores, excerpts, and traceable chunk IDs.
- Optional retrieval filters for jurisdiction, document type, and superseded-source handling.
- Source-status warnings for superseded, mixed-version, mixed-jurisdiction, or mixed-year evidence.
- Retrieval evaluation and mode ablation with sample questions and repeatable metrics.
- Tests for chunking, retrieval, citations, and no-result handling.
- Clear architecture, limitations, demo artifacts, and production next steps.

## Quickstart

From the repository root:

```bash
python scripts/generate_sample_data.py
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py
pytest tests/test_rag.py
streamlit run projects/aec-code-compliance-rag/app.py
```

The app runs locally without paid APIs. If `OPENAI_API_KEY` is not set, the assistant uses a deterministic local mock provider and still returns citation-bearing answers.

Optional Singapore public-source corpus:

```bash
python projects/aec-code-compliance-rag/scripts/download_public_sources.py
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py --corpus public
```

The downloaded PDFs/HTML text and generated manifest stay in `public_sources/downloaded/`, which is ignored by Git. The repository commits the source inventory and eval cases, not redistributed government PDFs.

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
- [`retrieval_eval_report.md`](demo_outputs/retrieval_eval_report.md)
- [`retrieval_ablation_summary.json`](demo_outputs/retrieval_ablation_summary.json)
- [`retrieval_ablation_report.md`](demo_outputs/retrieval_ablation_report.md)
- [`accessible_route_answer.md`](demo_outputs/accessible_route_answer.md)
- [`no_answer_failure_case.md`](demo_outputs/no_answer_failure_case.md)
- [`public_sources/`](demo_outputs/public_sources/) for optional Singapore public-source eval outputs after running the public corpus command.

Regenerate them with:

```bash
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py
```

## Features

- Markdown and text-based PDF document ingestion from `sample_data/`.
- Optional Singapore public-source downloader for BCA, URA, NEA, SCDF, LTA, PUB, and NParks reference documents.
- Source manifest loading from `sample_data/source_manifest.json`.
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
- Streamlit public/synthetic corpus switch and FastAPI query/retrieval endpoints for API-style review.
- Tests covering chunking, retrieval, citations, no-result handling, and eval scoring.

## Architecture And Evaluation Docs

- [`ARCHITECTURE.md`](ARCHITECTURE.md) explains the data flow, module boundaries, metadata contract, and production extension points.
- [`EVAL.md`](EVAL.md) explains the evaluation dataset, metrics, known failure modes, and how to interpret the sample results.
- [`LIMITATIONS.md`](LIMITATIONS.md), [`CASE_STUDY.md`](CASE_STUDY.md), and [`SYSTEM_CARD.md`](SYSTEM_CARD.md) define project boundaries and review context.

## How It Works

1. Synthetic markdown guidance, a generated PDF addendum, and `source_manifest.json` are loaded from `sample_data/`; alternatively, the public-source workflow loads downloaded Singapore official documents plus a generated source manifest.
2. Markdown files are split by headings and optional page markers such as `<!-- page: 2 -->`; PDFs are extracted page by page with `pypdf`.
3. Manifest records override or enrich document metadata before chunks are indexed.
4. Each chunk receives traceable metadata: source, title, source type, allowed use, section, heading, clause ID, page value, chunk ID, start word, end word, document version, jurisdiction, code year, and superseded status.
5. A local retriever ranks the eligible source subset for a question. The default app mode is hybrid TF-IDF/BM25; the eval script also compares TF-IDF, BM25, dense LSA, and hybrid modes.
6. The assistant returns an answer only from retrieved evidence, exposes structured citations, and warns when retrieved sources need version or jurisdiction review.
7. The evaluation script runs sample questions and writes metrics plus demo outputs.

## Tests

```bash
pytest tests/test_rag.py
```

The tests cover:

- Chunk metadata and page-marker parsing.
- Retrieval of the expected section.
- Dense LSA retrieval metadata and retrieval-mode ablation.
- Citation formatting and chunk IDs.
- Document-version, jurisdiction, and superseded-source metadata.
- Source manifest overrides and filtered retrieval behavior.
- Empty and no-result handling.
- Retrieval evaluation metrics.

## Optional Public-Source Review

The public corpus is designed to move the project beyond a toy RAG demo while keeping redistribution boundaries clean. It includes source metadata for:

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

```bash
uvicorn api:app --app-dir projects/aec-code-compliance-rag --reload
```

The API exposes `/health`, `/sources`, `/query`, `/retrieve`, and `/logs/recent`. Query logs are local SQLite records under `demo_outputs/` for inspection, not production telemetry.

## Limitations

- The default corpus is synthetic and intentionally small.
- The optional Singapore public corpus downloads official public documents locally, but it is still not a validated compliance engine.
- PDF ingestion is text-based and page-aware, but it does not handle scanned PDFs, OCR, table reconstruction, or layout geometry.
- TF-IDF, BM25, dense LSA, and hybrid modes are transparent and local. Optional embedding/reranking modes require `requirements-embeddings.txt` and model downloads.
- The local answer mode is deterministic and extractive; it is not a real expert model.
- The project does not certify against current building-code amendments, authority interpretations, project submissions, or professional review requirements.
- No real project, client, or construction data is included.

## Next Steps

- Improve PDF ingestion with layout-aware table extraction, OCR fallback, and clause-level parsing.
- Improve Singapore source refresh checks, amendment detection, and source inventory validation.
- Benchmark optional embedding and cross-encoder retrieval against the public-source eval set.
- Strengthen citation-faithfulness checks beyond the current deterministic lexical coverage check.
- Expand the evaluation set with negative questions, ambiguous jurisdiction cases, and adversarial wording.
- Add stronger conflict detection for contradictory source content and superseded clauses.
- Add an expert-review queue for uncertain answers.

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
