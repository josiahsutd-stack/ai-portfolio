# Technical Review Guide

This document is written for recruiters and technical reviewers. It summarizes what the flagship projects demonstrate, what is intentionally mocked or synthetic, and which implementation details are worth inspecting. The intended interpretation is: these are local, testable demos of engineering shape with clear production next steps, not inflated production claims.

## Flagship Projects

### Agentic Research Operations Assistant

- Review signal: planner-executor agent with local document retrieval, tool calls, citations, memory, and approval checkpoints.
- Architecture evidence: task -> plan -> tools -> retrieved evidence -> report -> human approval -> trace.
- Engineering rationale: deterministic tools make the agent inspectable and testable.
- Limitations to note: local documents only; no live web search or production workflow engine.
- Technical question supported: "How are hallucinations controlled?" Evidence in the project includes citations, retrieved context, approval checkpoints, and eval traces.
- Production extension: PDF ingestion, richer memory, retries, and SQLite trace storage.

### Multimodal VLM Visual QA Assistant

- Review signal: image QA workflow with mock VLM provider, structured JSON, confidence, uncertainty, and validation.
- Architecture evidence: image bytes -> validator -> provider abstraction -> schema response -> history/UI.
- Engineering rationale: the workflow separates product behavior from the model dependency.
- Limitations to note: mock mode validates the interface but does not perform real visual reasoning.
- Technical question supported: "How would this be evaluated?" Evidence to look for includes extraction accuracy, uncertainty calibration, visual hallucination cases, and schema validity.
- Production extension: OCR, real VLM provider integration, region grounding, and eval image sets.

### VLA Embodied Agent Simulator

- Review signal: language instructions and grid-world state are converted into safe action sequences.
- Architecture evidence: instruction parser -> safety-aware planner -> environment transitions -> episode trace.
- Engineering rationale: the simulation tests VLA reasoning shape without hardware risk.
- Limitations to note: no real robot, ROS, SLAM, or learned policy.
- Technical question supported: "What is VLA in this portfolio?" Evidence in the project shows a VLA-inspired mapping from language and state/visual observation to actions, limited honestly to simulation.
- Production extension: Gymnasium wrapper, richer visual renderer, learned policy, and robotics simulator bridge.

### MLOps Model Serving and Monitoring Platform

- Review signal: synthetic churn model with training, FastAPI prediction schema, drift checks, and monitoring dashboard.
- Architecture evidence: synthetic data -> training -> model metrics -> API -> drift report.
- Engineering rationale: the project shows deployment and monitoring shape without external services.
- Limitations to note: synthetic data and local in-memory model.
- Technical question supported: "How is model quality monitored?" Evidence to look for includes inference schema checks, drift metrics, model metadata, and the planned path to delayed labels.
- Production extension: SQLite logging, model registry files, alert thresholds, and retraining workflows.

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
- AEC RAG Assistant: chunking, retrieval, citations, incomplete-evidence handling, and TF-IDF limitations versus embedding retrieval.
- BIM Issue Detection Agent: deterministic rule checks before LLM explanation, issue reports, and AEC coordination workflow fit.
- Building Energy ML Pipeline: feature engineering, regression evaluation, model card, and energy-domain limitations.
