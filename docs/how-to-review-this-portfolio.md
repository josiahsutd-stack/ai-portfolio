# Portfolio Evidence Paths

## Five-Minute Screen

1. Read the root `README.md` selected-work table and claim boundaries.
2. Open `projects/aec-code-compliance-rag/EVAL.md`, `demo_outputs/public_sources/target_label_report.md`, `demo_outputs/public_sources/retrieval_eval_summary.json`, `demo_outputs/service_contract_report.md`, and `demo_outputs/service_reliability_report.md`.
3. Open `projects/vla-embodied-agent-simulator/EVAL.md` for learned-policy holdout results.
4. Open `projects/constraint-aware-massing-explorer/EVAL.md` and its option diagrams.
5. Use `docs/EVIDENCE_LEDGER.md` to trace displayed values to versioned artifacts.

## Fifteen-Minute Screen

```bash
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py
python projects/aec-code-compliance-rag/evaluate_service.py
python projects/aec-code-compliance-rag/evaluate_service_reliability.py
python projects/vla-embodied-agent-simulator/evaluate_vla.py
python projects/constraint-aware-massing-explorer/evaluate_massing.py
python -m pytest tests/test_rag.py tests/test_rag_service.py tests/test_vla_embodied_agent.py tests/test_massing_explorer.py
```

The commands use bundled synthetic data or a labeled public snapshot and require no paid APIs. Deterministic metrics, reports, traces, and diagrams are versioned for comparison.

## AEC Workflow Evidence

```bash
python projects/project-specification-copilot/evaluate_specification.py
python projects/qs-takeoff-tender-analysis/evaluate_qs.py
python integrations/aec-design-to-cost/run_workflow.py
python -m pytest tests/test_project_specification_copilot.py tests/test_qs_takeoff_tender_analysis.py tests/test_aec_workflow_integration.py
```

The [integration trace](../integrations/aec-design-to-cost/README.md) demonstrates one tested handoff from approved requirements to sourced massing inputs and a bounded schematic takeoff. Budget and accessibility remain under human review; tender analysis is not run. Every bundled conversation, site, rate, plan, and tender is synthetic and labeled.

## Optional Public AEC Check

```bash
python projects/aec-code-compliance-rag/scripts/download_public_sources.py
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py --corpus public
```

This path downloads official Singapore sources locally. It demonstrates provenance-aware ingestion and separates document, exact-chunk, and source-page retrieval. The chunk/page labels are candidate-authored; this is not document-currency validation, independent expert annotation, or authority approval.

## Evidence Hierarchy

1. AEC Code Compliance RAG: sole flagship and deepest retrieval/evaluation surface.
2. Construction Embodied Agent Simulator: strongest embodied-AI evidence.
3. Constraint-Aware Massing Explorer: strongest computational-design evidence.
4. Project Specification Copilot and QS Takeoff/Tender Workbench: supporting AEC workflow systems.
5. AEC design-to-cost integration: cross-project contract evidence, not a sixth project.
6. Work under [`experiments/`](../experiments/README.md): narrower generic and AEC baselines.

## Full Verification

```bash
python scripts/verify.py
```

The full check covers fixture generation, repository health, public claims and links, all imports, deterministic artifact generation, formatting, linting, and pytest.
