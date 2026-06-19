# Technical Review Guide

This document is written for recruiters and technical reviewers. It summarizes what the primary project and supporting review projects demonstrate, what is intentionally mocked or synthetic, and which implementation details are worth inspecting. The intended interpretation is: these are local, testable demos of engineering shape with clear next steps, not inflated production claims.

## Primary Review Project

### AEC Code Compliance RAG Assistant

- Review signal: source-grounded AEC RAG with section-aware chunking, chunk metadata, citation formatting, retrieval evaluation, demo outputs, tests, and explicit limitations.
- Architecture evidence: synthetic markdown guidance -> section-aware chunks -> hybrid TF-IDF/BM25 retrieval -> citation-bearing answer -> retrieval eval -> demo outputs.
- Engineering rationale: compliance-oriented AI should expose evidence, metadata, uncertainty, and no-result behavior before answer polish.
- Limitations to note: synthetic corpus, markdown page markers, local lexical retrieval baseline, no live building-code validation, and no professional compliance advice.
- Technical question supported: "How do you evaluate and cite an AEC RAG system?" Evidence includes `EVAL.md`, `ARCHITECTURE.md`, `evaluate_retrieval.py`, `demo_outputs/`, and `tests/test_rag.py`.
- Next extension: PDF ingestion, richer clause/version metadata, embedding retrieval, reranking, stronger answer-faithfulness checks, jurisdiction filters, and expert approval workflow.

## Supporting Review Projects

### Agentic Research Operations Assistant

- Review signal: planner-executor agent with local document retrieval, tool registry, per-tool traces, citations, memory, approval checkpoints, SQLite trace persistence, and trace evaluation.
- Architecture evidence: task -> plan -> tool registry/permissions -> retrieved evidence -> report -> human approval -> persisted trace -> trace eval.
- Engineering rationale: the agent keeps every step inspectable, permissioned, retryable, and auditable.
- Limitations to note: local documents only; no live web search or production workflow engine.
- Technical question supported: "How are hallucinations controlled?" Evidence in the project includes citations, retrieved context, approval checkpoints, tool traces, persisted runs, and eval findings.
- Next extension: PDF ingestion, web/search connectors, richer memory, role-based tool permissions, and richer eval suites.

### MLOps Model Serving and Monitoring Platform

- Review signal: synthetic churn model with training, model artifact, FastAPI prediction schema, SQLite inference logging, drift checks, and monitoring dashboard.
- Architecture evidence: synthetic data -> training -> model artifact/metadata -> API -> prediction log -> drift report/history.
- Engineering rationale: the project shows deployment and monitoring shape without external services.
- Limitations to note: synthetic data, local model artifact, and lightweight drift checks.
- Technical question supported: "How is model quality monitored?" Evidence to look for includes inference schema checks, SQLite prediction logs, drift metrics, model metadata, and the planned path to delayed labels.
- Next extension: MLflow-compatible registry, alert thresholds, retraining workflows, and real delayed labels.

### Fine-Tuning and LoRA Lab

- Review signal: dataset validation, split verification, LoRA config planning, mock-training honesty, and held-out eval template.
- Architecture evidence: synthetic instruction data -> validation -> train/validation split -> LoRA config -> mock training report -> evaluation template.
- Engineering rationale: adaptation work should start with dataset quality and evaluation design, not a fake training metric.
- Limitations to note: no tokenizer/model loading, no GPU training, no updated weights, no real accuracy claim.
- Next extension: PEFT trainer, real model config, held-out eval harness, adapter artifact storage, and safety review.

### Multimodal VLM Visual QA Assistant

- Review signal: image validation, prompt contract, structured output schema, mock provider, and optional hosted provider boundary.
- Architecture evidence: image bytes -> validator -> prompt builder -> provider -> Pydantic response -> UI/API.
- Engineering rationale: multimodal apps need schemas and uncertainty before real provider integration.
- Limitations to note: mock mode validates workflow but does not perform real visual reasoning; hosted mode requires a real API key and model access.
- Technical question supported: "How would this be evaluated?" Evidence to look for includes extraction accuracy, uncertainty calibration, visual hallucination cases, and schema validity.
- Next extension: OCR, region grounding, real eval images, visual hallucination tests, and latency monitoring.

### LLM Evals and Guardrails Platform

- Review signal: eval cases for prompt injection, structured output validity, and citation coverage.
- Architecture evidence: eval case -> guardrail checks -> scores -> findings -> dashboard/API.
- Engineering rationale: deterministic baseline evals are easy to run in CI and easy to inspect.
- Limitations to note: transparent rules are not a full red-team program.
- Technical question supported: "How are LLM systems made more reliable?" Evidence in the project includes eval sets, regression checks, structured-output validation, prompt-injection checks, and monitoring surfaces.
- Next extension: prompt versioning, model-graded evals, persisted results, and CI gating.

## Secondary Project Review Signals

- LLM Evals Guardrails: prompt-injection checks, structured-output validation, citation checks, and eval-result schema.
- Reinforcement Learning Portfolio: environment design, reward shaping, policy baselines, and the distinction between simulation and optimization claims.
- Deep Learning Vision Lab: synthetic dataset generation, metrics, model-card discipline, and the path from baseline to PyTorch CNN/U-Net.
- Recommender Ranking Engine: popularity versus content-based recommendations, ranking metrics, and product-facing explanations.
- Time-Series Anomaly Forecasting: moving-average baseline, Isolation Forest, alert thresholds, and time-aware evaluation.
- VLA Embodied Agent Simulator: language-to-action simulation, state/action traces, and honest hardware limitations.
- BIM Issue Detection Agent: deterministic rule checks before LLM explanation, issue reports, and AEC coordination workflow fit.
- Building Energy ML Pipeline: feature engineering, regression evaluation, model card, and energy-domain limitations.
