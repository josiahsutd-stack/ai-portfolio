# Interview Prep

Use this document to explain the portfolio honestly. The strongest answer is not "this is production"; it is "this is a local, testable demo of the engineering shape, with clear next steps."

## Flagship Projects

### Agentic Research Operations Assistant

- Summary: planner-executor agent with local document retrieval, tool calls, citations, memory, and approval checkpoints.
- Architecture: task -> plan -> tools -> retrieved evidence -> report -> human approval -> trace.
- Why this approach: deterministic tools make the agent inspectable and testable.
- Limitations: local documents only; no live web search or production workflow engine.
- Interview question: "How do you prevent hallucinations?" Strong answer: citations, local retrieved context, approval checkpoint, and eval traces.
- Extension: add PDF ingestion, richer memory, retries, and SQLite trace storage.

### Multimodal VLM Visual QA Assistant

- Summary: image QA workflow with mock VLM provider, structured JSON, confidence, uncertainty, and validation.
- Architecture: image bytes -> validator -> provider abstraction -> schema response -> history/UI.
- Why this approach: separates product workflow from model dependency.
- Limitations: mock mode does not perform real visual reasoning.
- Interview question: "How would you evaluate it?" Strong answer: extraction accuracy, uncertainty calibration, visual hallucination cases, and schema validity.
- Extension: add OCR, real VLM provider, region grounding, and eval image sets.

### VLA Embodied Agent Simulator

- Summary: language instruction and grid-world state are converted into safe action sequences.
- Architecture: instruction parser -> safety-aware planner -> environment transitions -> episode trace.
- Why this approach: tests VLA reasoning shape without hardware risk.
- Limitations: no real robot, ROS, SLAM, or learned policy.
- Interview question: "What is VLA here?" Strong answer: VLA-inspired mapping from language and state/visual observation to actions, honestly limited to simulation.
- Extension: add Gymnasium wrapper, richer visual renderer, and learned policy.

### MLOps Model Serving and Monitoring Platform

- Summary: synthetic churn model with training, FastAPI prediction schema, drift checks, and monitoring dashboard.
- Architecture: synthetic data -> training -> model metrics -> API -> drift report.
- Why this approach: shows deployment and monitoring shape without external services.
- Limitations: synthetic data and local in-memory model.
- Interview question: "How do you monitor model quality?" Strong answer: inference logs, schema validation, drift checks, and eventual delayed labels.
- Extension: add SQLite logging, model registry files, and alert thresholds.

### LLM Evals and Guardrails Platform

- Summary: evaluates prompt injection, structured output validity, and citation coverage.
- Architecture: eval case -> guardrail checks -> scores -> findings -> dashboard/API.
- Why this approach: deterministic baseline evals are easy to run in CI.
- Limitations: rules are not a full red-team program.
- Interview question: "How do you make LLM systems reliable?" Strong answer: eval sets, regression gates, structured-output validation, prompt-injection checks, and monitoring.
- Extension: add prompt versioning, model-graded evals, and persisted results.

## Secondary Projects

- Reinforcement Learning Portfolio: explain reward shaping, policy baselines, and why simulation comes before optimization claims.
- Deep Learning Vision Lab: explain synthetic dataset generation, metrics, and how a PyTorch CNN/U-Net would replace the baseline.
- Recommender Ranking Engine: explain popularity vs content-based recommendations and ranking metrics.
- Time-Series Anomaly Forecasting: explain moving-average baseline, Isolation Forest, and alert evaluation.
- Fine-Tuning LoRA Lab: explain dataset validation and compute-aware mock training before real GPU LoRA.
- AEC RAG Assistant: explain chunking, retrieval, citations, and limitations of TF-IDF versus embeddings.
- BIM Issue Detection Agent: explain deterministic rule checks before LLM explanation.
- Building Energy ML Pipeline: explain feature engineering, regression, and model cards.

