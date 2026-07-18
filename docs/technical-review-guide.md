# Technical Review Guide

This guide separates implementation evidence from portfolio framing. The repository contains one flagship, two role-defining projects, two substantial supporting systems, and fourteen smaller experiments or baselines.

## 1. AEC Code Compliance RAG - Flagship

**Implemented:** Markdown and PDF ingestion, page/section metadata, Singapore public-source manifests, source filters, TF-IDF/BM25/dense-LSA/hybrid retrieval, citation objects, status handling, retrieval ablation, failure analysis, demo answers, and focused tests.

**Inspect:** `src/aec_code_compliance_rag/`, `evaluate_retrieval.py`, `EVAL.md`, `ARCHITECTURE.md`, `demo_outputs/`, and `tests/test_rag.py`.

**Engineering question:** How does the system preserve provenance and choose between an answer, no evidence, and professional-review scope?

**Boundary:** The default 51-case set is synthetic. Optional public documents are downloaded locally and are not guaranteed current. There is no OCR, authority validation, professional advice, or compliance certification.

## 2. Construction Embodied Agent Simulator - Embodied AI Evidence

**Implemented:** Rule-based language-to-task parsing, procedural train/holdout grids, expert A* demonstrations, a real random-forest behavior-cloning policy, raw and safety-filtered rollout modes, action masks, intervention logs, closed-loop metrics, failure analysis, and replay traces.

**Inspect:** `environment.py`, `policies.py`, `learning.py`, `EVAL.md`, `demo_outputs/behavior_cloning_eval_report.md`, `demo_outputs/behavior_cloning_failure_analysis.md`, and `tests/test_vla_embodied_agent.py`.

**Engineering question:** Which safety failures are prevented by action masks and route planning, and which risks are absent from the simulator?

**Boundary:** The learned classifier consumes 24 engineered structured-state features. It is not a foundation VLA and does not establish perception, physics, ROS integration, hardware behavior, or physical safety.

## 3. Local Text Classification Lab - Model Training Evidence

**Implemented:** Fixed train/validation/test splits, TF-IDF features, logistic regression, dummy baseline, held-out metrics, confusion matrix, generated joblib artifacts, reports, and focused tests.

**Inspect:** `training.py`, `evaluate_model.py`, `demo_outputs/public_sms_metrics.json`, `demo_outputs/public_sms_confusion_matrix.json`, dataset source notes, and `tests/test_real_model_finetune_lab.py`.

**Engineering question:** How do the baseline, validation, and held-out test results differ, and where do the learned coefficients live?

**Boundary:** The public SMS subset contains 240 rows and the test split contains 40. This is classical ML, not transformer or LoRA training, and the result is not a benchmark claim.

## Supporting Systems

### Deterministic Research Workflow Assistant

Permissioned deterministic planning, local retrieval, citations, retries, approval gates, SQLite traces, and trace evaluation. It demonstrates inspectable agent control flow, not autonomous research or live web access.

### Local Model Serving And Monitoring Scaffold

Synthetic churn training, generated artifact metadata, FastAPI validation, SQLite prediction logs, mean-shift and PSI-style drift checks, and monitoring reports. It demonstrates local lifecycle structure, not deployed platform ownership.

## Experiments And Baselines

The visual-provider contract, LoRA data/configuration validator, vision threshold model, sequential-decision environments, ranking and time-series baselines, BIM and energy checks, construction metadata classifier, spatial scorer, job matcher, and smaller robotics simulations provide supporting breadth. Their README limitations are part of the evidence; none should be interpreted as equal depth to the flagship.

## Verification

```bash
python scripts/verify.py
```

The verifier scans public claims and links, imports all project modules, regenerates deterministic review artifacts, checks formatting and linting, and runs the full test suite.
