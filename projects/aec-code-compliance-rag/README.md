# AEC Code Compliance RAG Assistant

Primary flagship project for this AI engineering portfolio.

This is a local, source-grounded retrieval assistant for synthetic AEC guidance. It demonstrates the engineering shape behind a compliance-oriented RAG workflow: document chunking, metadata preservation, transparent retrieval, citation formatting, evaluation questions, demo outputs, and failure handling.

It does not use real project data, customer data, or live building codes. The included documents are synthetic demo data and the outputs are not legal, code, engineering, or professional compliance advice.

## Problem

Architecture, engineering, and construction teams often need to search across code clauses, planning notes, accessibility guidance, drawing QA standards, and internal assumptions before issuing work. A generic chatbot is risky in that setting because it can answer confidently without showing where the evidence came from.

This project focuses on the safer applied AI pattern: retrieve evidence first, show citations, expose retrieval metadata, and clearly state when the local demo corpus has no answer.

## Why It Matters

The project connects AI engineering with the built environment. It shows how a junior/applied AI engineer can structure a domain RAG system without pretending the demo is a deployed compliance product.

Key reviewer signals:

- Evidence-first retrieval over synthetic AEC guidance.
- Chunk metadata for section, heading, clause ID, page marker, chunk ID, and word offsets.
- Citation objects that include readable references, scores, excerpts, and traceable chunk IDs.
- Retrieval evaluation with sample questions and repeatable metrics.
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

Try these questions:

- What clear width should be checked for high traffic accessible routes?
- What doorway and threshold checks apply to accessible rooms?
- What should be included for long residential corridors?
- What daylight risks should west glazing trigger?
- Which assumptions should be logged before a planning submission?

Generated reviewer artifacts are in [`demo_outputs/`](demo_outputs/):

- [`retrieval_eval_summary.json`](demo_outputs/retrieval_eval_summary.json)
- [`retrieval_eval_report.md`](demo_outputs/retrieval_eval_report.md)
- [`accessible_route_answer.md`](demo_outputs/accessible_route_answer.md)
- [`no_answer_failure_case.md`](demo_outputs/no_answer_failure_case.md)

Regenerate them with:

```bash
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py
```

## Features

- Markdown document ingestion from `sample_data/`.
- Section-aware chunking with overlap.
- Metadata fields for heading, clause ID, page marker, chunk ID, and word offsets.
- Local TF-IDF retrieval as an inspectable vector-search stand-in.
- Deterministic no-API answer mode plus optional OpenAI-compatible provider through shared portfolio utilities.
- Citation formatting with references like `[C1] mock_aec_guidance.md > Accessible Routes`.
- Retrieval evaluation over sample questions.
- No-answer evaluation for unsupported compliance questions.
- Demo output generation for reviewers.
- Tests covering chunking, retrieval, citations, no-result handling, and eval scoring.

## Architecture And Evaluation Docs

- [`ARCHITECTURE.md`](ARCHITECTURE.md) explains the data flow, module boundaries, metadata contract, and production extension points.
- [`EVAL.md`](EVAL.md) explains the evaluation dataset, metrics, known failure modes, and how to interpret the sample results.

## How It Works

1. Synthetic markdown guidance is loaded from `sample_data/`.
2. The chunker splits by markdown headings and optional page markers such as `<!-- page: 2 -->`.
3. Each chunk receives traceable metadata: source, section, heading, clause ID, page marker, chunk ID, start word, and end word.
4. A local TF-IDF store retrieves the top-k chunks for a question.
5. The assistant returns an answer only from retrieved evidence and exposes structured citations.
6. The evaluation script runs sample questions and writes metrics plus demo outputs.

## Tests

```bash
pytest tests/test_rag.py
```

The tests cover:

- Chunk metadata and page-marker parsing.
- Retrieval of the expected section.
- Citation formatting and chunk IDs.
- Empty and no-result handling.
- Retrieval evaluation metrics.

## Limitations

- The corpus is synthetic and intentionally small.
- The page values are demo markdown markers, not parsed PDF page numbers.
- TF-IDF is transparent and local, but weaker than embedding retrieval or hybrid search.
- The local answer mode is deterministic and extractive; it is not a real expert model.
- The project does not validate against live jurisdictions, current building codes, amendments, or professional review requirements.
- No real project, client, or construction data is included.

## Next Steps

- Add PDF ingestion with real page extraction and clause-level parsing.
- Replace or augment TF-IDF with hybrid retrieval: BM25, embeddings, and reranking.
- Add citation-faithfulness checks that compare answer claims to retrieved evidence.
- Expand the evaluation set with negative questions, ambiguous jurisdiction cases, and adversarial wording.
- Add versioned document metadata for jurisdiction, code year, issue date, and superseded clauses.
- Add a reviewer workflow where uncertain answers are routed to a qualified professional.

## What This Proves To Employers

- Practical RAG system design for a real domain workflow.
- Source-grounded answer design and citation ergonomics.
- Retrieval evaluation and failure analysis discipline.
- Local-first engineering that reviewers can run without paid APIs.
- Honest separation between demo behavior and production compliance requirements.

## Engineering Notes

- The system uses deterministic chunk IDs and metadata so retrieval results can be inspected and tested.
- Synthetic page markers are preserved to show the metadata contract that a PDF parser would fill in later.
- The assistant refuses empty questions and returns a no-evidence response when retrieval has no matching chunks.
- The local TF-IDF store is chosen for portability and transparency; it is a baseline, not the final retrieval method for a real compliance product.

## Technical Review Discussion Points

- How should retrieval be evaluated before an AEC assistant is trusted by practitioners?
- What metadata is required for citations to be auditable?
- Where should expert review sit in a compliance workflow?
- How would hybrid retrieval, reranking, and citation-faithfulness checks change the architecture?
- Which claims can this demo support, and which claims would require real data, legal review, and production monitoring?
