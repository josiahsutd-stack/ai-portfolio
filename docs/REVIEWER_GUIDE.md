# Reviewer Guide

This guide gives recruiters and technical interviewers a short path through the repository without treating project count as project depth.

## Fifteen-Minute Screen

| Order | Project | Evidence to inspect | Interpretation limit |
| --- | --- | --- | --- |
| 1 | `projects/aec-code-compliance-rag` | `EVAL.md`, `ARCHITECTURE.md`, `demo_outputs/`, `tests/test_rag.py` | Flagship retrieval system; not compliance certification. |
| 2 | `projects/vla-embodied-agent-simulator` | procedural splits, fitted behavior-cloning model, raw/filtered holdout metrics, failure analysis, replay traces, and focused tests | Structured embodied-agent simulation; not a foundation VLA or hardware. |
| 3 | `projects/real-model-finetune-lab` | held-out metrics, confusion matrix, training code, focused tests | Real classical-model fitting on small datasets; no transformer training. |

Deterministic Research Workflow Assistant and Local Model Serving and Monitoring are the strongest supporting workflow projects. The other fourteen projects are narrower experiments or baselines.

## Fast Verification

```bash
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py
python projects/vla-embodied-agent-simulator/evaluate_vla.py
python projects/real-model-finetune-lab/evaluate_model.py
python -m pytest tests/test_rag.py tests/test_vla_embodied_agent.py tests/test_real_model_finetune_lab.py
```

Full repository check:

```bash
python scripts/verify.py
```

The [headline evidence ledger](EVIDENCE_LEDGER.md) maps each displayed metric to an exact JSON path, versioned artifact, evaluation scope, and reproduction command.

## Role-Specific Paths

- Applied AI / LLM: AEC RAG, Deterministic Research Workflow Assistant, then Local Text Classification Lab.
- Embodied AI / robotics: Construction Embodied Agent Simulator, AEC RAG for construction-domain grounding, then Construction Grid Route Planner.
- ML / MLOps: Local Text Classification Lab, Local Model Serving and Monitoring, then Time-Series Forecast and Anomaly Baselines.
- Multimodal / CV: Visual QA Provider Contract and Vision Threshold Baseline are experiments only; the former proves an interface contract and the latter a deterministic image baseline, not deep-learning training.

## Technical Questions Supported By Evidence

- How does authority and page metadata move from downloaded AEC documents into retrieved citations?
- Why compare TF-IDF, BM25, dense LSA, and hybrid retrieval before adding hosted embeddings?
- How does the AEC assistant distinguish an answer from no evidence or professional-review scope?
- How does the safety filter change learned-policy success and unsafe-action rates relative to raw behavior cloning and the deterministic A* reference?
- Where are fitted model parameters created, and how are baseline, validation, and held-out test metrics separated?
- How do denied tools, retries, approval gates, and failed calls appear in an agent trace?
- What can a local drift simulation reveal, and what would require delayed labels or production telemetry?

## Ownership Check

The strongest ownership evidence would be a live change to retrieval behavior, a new embodied-agent scenario and regression test, or a modification to the training split followed by an explanation of the resulting metrics. README fluency alone is not treated as ownership evidence.
