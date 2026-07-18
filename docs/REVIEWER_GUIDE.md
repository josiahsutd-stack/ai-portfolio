# Reviewer Guide

## Fifteen-Minute Technical Screen

| Order | Project | Evidence to inspect | Interpretation limit |
| --- | --- | --- | --- |
| 1 | `projects/aec-code-compliance-rag` | architecture, public provenance, retrieval ablation, failure analysis, demo answers, local service contract, fixed reliability workload, durable telemetry, and focused tests | Flagship retrieval system; in-process reliability evidence is not compliance certification, deployment, uptime, or capacity evidence. |
| 2 | `projects/vla-embodied-agent-simulator` | engineered, semantic-raster, egocentric-state, and rendered-RGB comparison; unseen appearance shift; 96-scenario holdout; 12-scenario MuJoCo command replay; raw/filtered metrics; failures; model cards; and tests | RGB pixels are state-rendered and filters see full rules; physics is planar contact replay, not physical-camera, mobile-robot-controller, ROS, or hardware evidence. |
| 3 | `projects/constraint-aware-massing-explorer` | hard constraints, proxy objectives, Pareto ranking, baseline evaluation, diagrams, and tests | Rectangular proxy geometry; not professional design. |

The specification and QS projects extend the same AEC workflow with auditability and commercial-review boundaries. Their [cross-project integration](../integrations/aec-design-to-cost/README.md) is executable and tested; it is not counted as a sixth selected project. Fourteen narrower baselines remain under [`experiments/`](../experiments/README.md).

## Fast Verification

```bash
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py
python projects/aec-code-compliance-rag/evaluate_service.py
python projects/aec-code-compliance-rag/evaluate_service_reliability.py
python projects/vla-embodied-agent-simulator/evaluate_vla.py
python projects/constraint-aware-massing-explorer/evaluate_massing.py
python integrations/aec-design-to-cost/run_workflow.py
python -m pytest tests/test_rag.py tests/test_rag_service.py tests/test_vla_embodied_agent.py tests/test_massing_explorer.py tests/test_aec_workflow_integration.py
```

Full repository check: `python scripts/verify.py`.

The [evidence ledger](EVIDENCE_LEDGER.md) maps displayed metrics to versioned artifacts, evaluation scope, and reproduction commands.

## Role-Specific Evidence

- Applied AEC AI: AEC RAG, Massing Explorer, Specification Copilot, then QS Workbench.
- Embodied AI and robotics: Construction Embodied Agent, Grid Route Planner, then Robot Telemetry Monitor.
- Retrieval and LLM systems: AEC RAG, Specification Copilot state machine, then the deterministic research-workflow experiment.
- ML and MLOps: the text-classification and model-monitoring experiments retain focused classical-model evidence but are not selected work.
- Multimodal and CV: the visual-provider and threshold-model experiments prove only bounded interface and baseline behavior.

## Technical Questions Supported By Evidence

- How does page and authority metadata move from public AEC documents into citations?
- Why compare lexical, probabilistic, latent-semantic, and hybrid retrieval locally?
- How do raw and filtered policies differ in discrete rollouts and planar contact replay, and what does the unseen RGB palette reveal about visual brittleness?
- How are hard massing constraints separated from editable proxy objectives?
- How do message ids, requirement versions, approval scopes, and draft clauses remain traceable?
- How are shared walls deduplicated, rate units validated, and tender exceptions explained?
- Which approved requirements cross the integration boundary, which remain under human review, and which invalid handoffs fail closed?

## Ownership Check

High-signal ownership evidence is a live change to retrieval behavior, a new embodied or massing scenario with a regression test, or a modified integration fixture followed by a correct explanation of changed sources, outputs, and rejections. README fluency alone is not ownership evidence.
