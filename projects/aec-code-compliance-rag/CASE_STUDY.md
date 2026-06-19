# Case Study: Synthetic AEC RAG Assistant

## Problem

AEC teams often need source-grounded answers across guidance, drawing assumptions, and review notes. A generic chatbot is risky when it gives answers without evidence.

## Local System

The project ingests synthetic markdown documents, a generated text-based PDF addendum, and a source manifest, creates section/page-aware chunks, preserves metadata, supports source-filtered retrieval, formats citations, applies deterministic abstention rules, and writes evaluation artifacts.

## Retrieval Strategy

TF-IDF and BM25 remain transparent lexical baselines. Dense LSA adds a local dense baseline without model downloads. Hybrid retrieval merges lexical result sets and keeps component scores in metadata.

## Citation Strategy

Answers include citation markers such as `[C1]`, and citations expose source, title, source type, allowed use, section, clause ID, PDF page or markdown page marker, chunk ID, score, and excerpt.

## Abstention Policy

The assistant returns `no_evidence`, `unsupported_scope`, or `needs_professional_review` for empty questions, weak evidence, live/current-code requests, jurisdictional questions, or professional sign-off requests.

## Evaluation

`python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py` runs 51 synthetic cases and writes summary metrics, a retrieval-mode ablation, failure analysis, and sample answers under `demo_outputs/`.

## Production Extension

A production version would need real source authorization, manifest validation against approved source inventories, layout-aware PDF/OCR parsing, human expert review, monitoring, and stronger answer faithfulness evaluation.
