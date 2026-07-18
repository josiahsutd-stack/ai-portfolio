# How To Review This Portfolio

## Five-Minute Path

1. Read the root `README.md` evidence table and boundaries.
2. Open `projects/aec-code-compliance-rag/EVAL.md`.
3. Inspect `projects/aec-code-compliance-rag/demo_outputs/retrieval_ablation_report.md`.
4. Skim `tests/test_rag.py` for retrieval, citation, and abstention coverage.
5. Choose either the VLA simulator or real-model lab based on the target role.

## Fifteen-Minute Path

```bash
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py
python projects/vla-embodied-agent-simulator/evaluate_vla.py
python projects/real-model-finetune-lab/evaluate_model.py
python -m pytest tests/test_rag.py tests/test_vla_embodied_agent.py tests/test_real_model_finetune_lab.py
```

The commands use bundled synthetic data or a labeled public subset and require no paid APIs. Generated model binaries and runtime databases are ignored by Git; deterministic metrics, reports, and traces are versioned for comparison.

## Optional Public AEC Check

```bash
python projects/aec-code-compliance-rag/scripts/download_public_sources.py
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py --corpus public
```

This path downloads official Singapore sources locally. It demonstrates provenance-aware ingestion and retrieval, not document-currency validation or authority approval.

## Evidence Hierarchy

1. AEC Code Compliance RAG: sole flagship and deepest code/evaluation surface.
2. VLA Embodied Agent Simulator: strongest embodied-AI evidence, bounded to a deterministic 2D environment.
3. Real Model Fine-Tune Lab: clearest proof that model parameters are actually fitted and evaluated.
4. Agentic Research Ops and MLOps Serving and Monitoring: substantial supporting workflow systems.
5. Remaining projects: narrower experiments and baselines.

## Full Verification

```bash
python scripts/verify.py
```

The full check covers fixture generation, repository health, claim and link scans, project imports, deterministic review-artifact generation, formatting, linting, and pytest.
