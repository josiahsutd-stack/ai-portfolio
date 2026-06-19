# Case Study: Synthetic AEC RAG Assistant

## Problem

AEC teams often need source-grounded answers across guidance, drawing assumptions, and review notes. A generic chatbot is risky when it gives answers without evidence.

## Local System

The project ingests synthetic markdown documents, creates section-aware chunks, preserves metadata, retrieves with hybrid TF-IDF/BM25, formats citations, applies deterministic abstention rules, and writes evaluation artifacts.

## Retrieval Strategy

TF-IDF remains as a transparent baseline. BM25 adds lexical ranking with document-length normalization. Hybrid retrieval merges both result sets and keeps component scores in metadata.

## Citation Strategy

Answers include citation markers such as `[C1]`, and citations expose source, section, clause ID, page marker, chunk ID, score, and excerpt.

## Abstention Policy

The assistant returns `no_evidence`, `unsupported_scope`, or `needs_professional_review` for empty questions, weak evidence, live/current-code requests, jurisdictional questions, or professional sign-off requests.

## Evaluation

`python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py` runs 50 synthetic cases and writes summary metrics, failure analysis, and sample answers under `demo_outputs/`.

## Production Extension

A production version would need real source authorization, PDF/page parsing, jurisdiction and code-year metadata, human expert review, monitoring, and stronger answer faithfulness evaluation.
