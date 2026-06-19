# Reviewer Guide

This guide is written for recruiters and technical interviewers reviewing the repository under time pressure.

## Fast Screen

The clearest evidence is concentrated in:

1. `projects/aec-code-compliance-rag`
2. `projects/agentic-research-ops-assistant`
3. `projects/mlops-model-serving-monitoring`

The remaining projects broaden the domain range but should be treated as supporting prototypes or experiments.

## Verification Commands

```bash
python scripts/generate_review_artifacts.py
python projects/aec-code-compliance-rag/scripts/download_public_sources.py
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py --corpus public
python -m pytest
python scripts/verify.py
```

## Code Worth Inspecting

- AEC RAG: public-source downloader, page-aware chunking, source filters, retrieval ablation, answer status, citation checks, evaluation script.
- Agent: deterministic planner, tool retry handling, denied-tool traces, SQLite persistence.
- MLOps: schema validation, metrics, artifact metadata, prediction logs, drift simulation.

## Interview Questions

- Explain the AEC RAG path from Singapore public source inventory to downloaded PDF/HTML snapshot to cited answer.
- Explain why TF-IDF, BM25, and dense LSA are used as local baselines before hosted embeddings or reranking.
- Show an unsupported-scope or no-evidence AEC question.
- Explain why the project can retrieve from BCA/URA/NEA/SCDF/LTA/PUB/NParks documents but still cannot certify compliance.
- Explain agent retry behavior and how failed tools appear in the trace.
- Explain the MLOps prediction schema and how impossible values are rejected.
- Explain what the drift report can and cannot prove.

## Ownership Evidence

Strong ownership would mean the candidate can modify retrieval behavior, debug an eval failure, explain a trace, add a test, refresh the Singapore source corpus, and discuss tradeoffs without relying on README language.
