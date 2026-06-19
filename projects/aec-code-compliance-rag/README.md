# AEC Code Compliance RAG Assistant

Primary review project for this AI engineering portfolio.

This is a local, source-grounded retrieval assistant for synthetic AEC guidance. It demonstrates the engineering shape behind a compliance-oriented RAG workflow: document chunking, source manifests, metadata-filtered retrieval, citation formatting, evaluation questions, demo outputs, and failure handling.

It does not use real project data, customer data, or live building codes. The included documents are synthetic demo data and the outputs are not legal, code, engineering, or professional compliance advice.

## Problem

Architecture, engineering, and construction teams often need to search across code clauses, planning notes, accessibility guidance, drawing QA standards, and internal assumptions before issuing work. A generic chatbot is risky in that setting because it can answer confidently without showing where the evidence came from.

This project focuses on a safer applied AI pattern: retrieve evidence first, show citations, expose retrieval metadata, and clearly state when the local demo corpus has no answer.

## Why It Matters

The project connects AI engineering with the built environment. It shows how a junior/applied AI engineer can structure a domain RAG system without pretending the demo is a deployed compliance product.

Key reviewer signals:

- Evidence-first retrieval over synthetic AEC guidance.
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

## Demo

```bash
streamlit run projects/aec-code-compliance-rag/app.py
```

![AEC RAG Streamlit demo](../../docs/assets/screenshots/aec-rag-demo.png)

Try these questions:

- What clear width should be checked for high traffic accessible routes?
- What doorway and threshold checks apply to accessible rooms?
- What should be included for long residential corridors?
- What daylight risks should west glazing trigger?
- Which assumptions should be logged before a planning submission?
- What should PDF extracted accessible parking notes record for wet-weather transfers?

Generated reviewer artifacts are in [`demo_outputs/`](demo_outputs/):

- [`retrieval_eval_summary.json`](demo_outputs/retrieval_eval_summary.json)
- [`retrieval_eval_report.md`](demo_outputs/retrieval_eval_report.md)
- [`retrieval_ablation_summary.json`](demo_outputs/retrieval_ablation_summary.json)
- [`retrieval_ablation_report.md`](demo_outputs/retrieval_ablation_report.md)
- [`accessible_route_answer.md`](demo_outputs/accessible_route_answer.md)
- [`no_answer_failure_case.md`](demo_outputs/no_answer_failure_case.md)

Regenerate them with:

```bash
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py
```

## Features

- Markdown and text-based PDF document ingestion from `sample_data/`.
- Source manifest loading from `sample_data/source_manifest.json`.
- Section-aware chunking with overlap.
- Metadata fields for title, source type, allowed use, heading, clause ID, PDF page or markdown page marker, chunk ID, and word offsets.
- Per-query source filters for jurisdiction, source type, and superseded-source exclusion.
- Local TF-IDF, BM25, dense LSA, and hybrid retrieval modes.
- Retrieval ablation report comparing modes over the same synthetic eval set.
- Deterministic no-API answer mode plus optional OpenAI-compatible provider through shared portfolio utilities.
- Citation formatting with references like `[C1] mock_aec_guidance.md > Accessible Routes`.
- Source-status analysis that flags retrieved evidence requiring version/jurisdiction review.
- Retrieval evaluation over sample questions.
- No-answer evaluation for unsupported compliance questions.
- Demo output generation for reviewers.
- Tests covering chunking, retrieval, citations, no-result handling, and eval scoring.

## Architecture And Evaluation Docs

- [`ARCHITECTURE.md`](ARCHITECTURE.md) explains the data flow, module boundaries, metadata contract, and production extension points.
- [`EVAL.md`](EVAL.md) explains the evaluation dataset, metrics, known failure modes, and how to interpret the sample results.
- [`LIMITATIONS.md`](LIMITATIONS.md), [`CASE_STUDY.md`](CASE_STUDY.md), and [`SYSTEM_CARD.md`](SYSTEM_CARD.md) define project boundaries and review context.

## How It Works

1. Synthetic markdown guidance, a generated PDF addendum, and `source_manifest.json` are loaded from `sample_data/`.
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

## Limitations

- The corpus is synthetic and intentionally small.
- PDF ingestion is text-based and page-aware, but it does not handle scanned PDFs, OCR, table reconstruction, or layout geometry.
- TF-IDF, BM25, dense LSA, and hybrid modes are transparent and local, but weaker than production embedding retrieval or neural reranking.
- The local answer mode is deterministic and extractive; it is not a real expert model.
- The project does not validate against live jurisdictions, current building codes, amendments, or professional review requirements.
- No real project, client, or construction data is included.

## Next Steps

- Improve PDF ingestion with layout-aware table extraction, OCR fallback, and clause-level parsing.
- Validate manifest entries against an authorized source inventory when using real documents.
- Add hosted/local embedding models and stronger reranking if local hardware or provider access is appropriate.
- Strengthen citation-faithfulness checks beyond the current deterministic lexical coverage check.
- Expand the evaluation set with negative questions, ambiguous jurisdiction cases, and adversarial wording.
- Add stronger conflict detection for contradictory source content and superseded clauses.
- Add a reviewer workflow where uncertain answers are routed to a qualified professional.

## Reviewer Signal

- Practical RAG system design for a domain workflow.
- Source-grounded answer design and citation ergonomics.
- Retrieval evaluation and failure analysis discipline.
- Local-first engineering that reviewers can run without paid APIs.
- Honest separation between demo behavior and production compliance requirements.

## Engineering Notes

- The system uses deterministic chunk IDs and metadata so retrieval results can be inspected and tested.
- `source_manifest.json` makes document status explicit instead of relying only on file headers.
- Markdown page markers and extracted PDF page numbers use the same citation metadata contract.
- The assistant refuses empty questions and returns a no-evidence response when retrieval has no matching chunks.
- The included retrieval modes are portable baselines, not final retrieval choices for a real compliance product.

## Technical Review Discussion Points

- How should retrieval be evaluated before an AEC assistant is trusted by practitioners?
- What metadata is required for citations to be auditable?
- Where should expert review sit in a compliance workflow?
- How would embedding retrieval, reranking, and stronger citation-faithfulness checks change the architecture?
- Which claims can this demo support, and which claims would require real data, legal review, and production monitoring?
