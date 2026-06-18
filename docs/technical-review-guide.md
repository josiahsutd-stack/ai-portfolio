# Technical Review Guide

This document is written for recruiters and technical reviewers. It summarizes what the flagship projects demonstrate, what is intentionally mocked or synthetic, and which implementation details are worth inspecting. The intended interpretation is: these are local, testable demos of engineering shape with clear production next steps, not inflated production claims.

## Flagship Projects

### AEC Code Compliance RAG Assistant

- Review signal: built-environment document assistant with retrieval, citations, and cautious incomplete-evidence handling.
- Architecture evidence: markdown guidance -> chunking -> local vector-style retrieval -> grounded answer -> source citations.
- Engineering rationale: source grounding is more important than answer fluency in compliance-adjacent workflows.
- Limitations to note: synthetic guidance and TF-IDF retrieval; this is not legal, code, or professional compliance advice.
- Technical question supported: "How is hallucination risk reduced?" Evidence includes citations, retrieved snippets, source scores, and no-evidence fallback behavior.
- Production extension: public-code/planning document ingestion, embedding retrieval, retrieval evals, and expert review workflow.

### Agentic Research Operations Assistant

- Review signal: planner-executor agent with local document retrieval, tool calls, citations, memory, and approval checkpoints.
- Architecture evidence: task -> plan -> tools -> retrieved evidence -> report -> human approval -> trace.
- Engineering rationale: deterministic tools make the agent inspectable and testable.
- Limitations to note: local documents only; no live web search or production workflow engine.
- Technical question supported: "How are hallucinations controlled?" Evidence in the project includes citations, retrieved context, approval checkpoints, and eval traces.
- Production extension: PDF ingestion, richer memory, retries, and SQLite trace storage.

### Multimodal VLM Visual QA Assistant

- Review signal: image QA workflow with mock mode, optional OpenAI-compatible hosted provider, structured JSON, confidence, uncertainty, and validation.
- Architecture evidence: image bytes -> validator -> provider abstraction -> hosted or mock response -> schema response -> history/UI.
- Engineering rationale: the workflow separates product behavior from the model dependency.
- Limitations to note: mock mode validates the interface but does not perform real visual reasoning; hosted mode requires a real API key and model access.
- Technical question supported: "How would this be evaluated?" Evidence to look for includes extraction accuracy, uncertainty calibration, visual hallucination cases, and schema validity.
- Production extension: OCR, region grounding, eval image sets, local model backends, and latency testing.

### MLOps Model Serving and Monitoring Platform

- Review signal: synthetic churn model with training, model artifact, FastAPI prediction schema, SQLite inference logging, drift checks, and monitoring dashboard.
- Architecture evidence: synthetic data -> training -> model artifact/metadata -> API -> prediction log -> drift report/history.
- Engineering rationale: the project shows deployment and monitoring shape without external services.
- Limitations to note: synthetic data, local model artifact, and lightweight drift checks.
- Technical question supported: "How is model quality monitored?" Evidence to look for includes inference schema checks, SQLite prediction logs, drift metrics, model metadata, and the planned path to delayed labels.
- Production extension: MLflow-compatible registry, alert thresholds, retraining workflows, and real delayed labels.

### LLM Evals and Guardrails Platform

- Review signal: eval cases for prompt injection, structured output validity, and citation coverage.
- Architecture evidence: eval case -> guardrail checks -> scores -> findings -> dashboard/API.
- Engineering rationale: deterministic baseline evals are easy to run in CI and easy to inspect.
- Limitations to note: transparent rules are not a full red-team program.
- Technical question supported: "How are LLM systems made more reliable?" Evidence in the project includes eval sets, regression checks, structured-output validation, prompt-injection checks, and monitoring surfaces.
- Production extension: prompt versioning, model-graded evals, persisted results, and CI gating.

## Secondary Project Review Signals

- Reinforcement Learning Portfolio: environment design, reward shaping, policy baselines, and the distinction between simulation and optimization claims.
- Deep Learning Vision Lab: synthetic dataset generation, metrics, model-card discipline, and the path from baseline to PyTorch CNN/U-Net.
- Recommender Ranking Engine: popularity versus content-based recommendations, ranking metrics, and product-facing explanations.
- Time-Series Anomaly Forecasting: moving-average baseline, Isolation Forest, alert thresholds, and time-aware evaluation.
- Fine-Tuning LoRA Lab: dataset validation, LoRA configuration, mock training, and compute-aware workflow design.
- VLA Embodied Agent Simulator: language-to-action simulation, state/action traces, and honest hardware limitations.
- BIM Issue Detection Agent: deterministic rule checks before LLM explanation, issue reports, and AEC coordination workflow fit.
- Building Energy ML Pipeline: feature engineering, regression evaluation, model card, and energy-domain limitations.
