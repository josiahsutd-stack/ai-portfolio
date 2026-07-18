# Portfolio Evidence Paths

## Five-Minute Screen

1. Read the root `README.md` selected-work table and claim boundaries.
2. Open `projects/aec-code-compliance-rag/EVAL.md` and `demo_outputs/public_evaluation_summary.json`.
3. Open `projects/vla-embodied-agent-simulator/EVAL.md` for learned-policy holdout results.
4. Open `projects/constraint-aware-massing-explorer/EVAL.md` and its option diagrams.
5. Use `docs/EVIDENCE_LEDGER.md` to trace displayed values to versioned artifacts.

## Fifteen-Minute Screen

```bash
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py
python projects/vla-embodied-agent-simulator/evaluate_vla.py
python projects/constraint-aware-massing-explorer/evaluate_massing.py
python -m pytest tests/test_rag.py tests/test_vla_embodied_agent.py tests/test_massing_explorer.py
```

The commands use bundled synthetic data or a labeled public snapshot and require no paid APIs. Deterministic metrics, reports, traces, and diagrams are versioned for comparison.

## AEC Workflow Evidence

```bash
python projects/project-specification-copilot/evaluate_specification.py
python projects/qs-takeoff-tender-analysis/evaluate_qs.py
python -m pytest tests/test_project_specification_copilot.py tests/test_qs_takeoff_tender_analysis.py
```

These supporting systems connect role-tagged communication to approved requirements, massing constraints, measured geometry, cost provenance, and tender exceptions. Every bundled conversation, site, rate, and tender is synthetic and labeled.

## Optional Public AEC Check

```bash
python projects/aec-code-compliance-rag/scripts/download_public_sources.py
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py --corpus public
```

This path downloads official Singapore sources locally. It demonstrates provenance-aware ingestion and retrieval, not document-currency validation or authority approval.

## Evidence Hierarchy

1. AEC Code Compliance RAG: sole flagship and deepest retrieval/evaluation surface.
2. Construction Embodied Agent Simulator: strongest embodied-AI evidence.
3. Constraint-Aware Massing Explorer: strongest computational-design evidence.
4. Project Specification Copilot and QS Takeoff/Tender Workbench: supporting AEC workflow systems.
5. Work under [`experiments/`](../experiments/README.md): narrower generic and AEC baselines.

## Full Verification

```bash
python scripts/verify.py
```

The full check covers fixture generation, repository health, public claims and links, all imports, deterministic artifact generation, formatting, linting, and pytest.
