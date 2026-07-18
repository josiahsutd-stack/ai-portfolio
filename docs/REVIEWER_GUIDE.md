# Reviewer Guide

## Fifteen-Minute Technical Screen

Each selected project opens with a generated system map using the same reading order: implemented stages, measured evidence, failure or control boundary, and required human review. The [system-map index](architecture-diagrams.md) collects those views without claiming cross-project behavior that has not been executed.

| Order | Project | Evidence to inspect | Interpretation limit |
| --- | --- | --- | --- |
| 1 | `projects/aec-code-compliance-rag` | architecture, public provenance, document-versus-exact retrieval metrics, target-label audit, fixed-case uncertainty, ablation, failure analysis, demo answers, local service contract, fixed reliability workload, durable telemetry, and focused tests | Flagship retrieval system; chunk/page targets are candidate-authored rather than expert labels, intervals are not external validity, and in-process reliability evidence is not compliance certification, deployment, uptime, or capacity evidence. |
| 2 | `projects/vla-embodied-agent-simulator` | engineered, semantic-raster, egocentric-state, and rendered-RGB comparison; unseen appearance shift; 96-scenario holdout; 12-scenario MuJoCo command replay; raw/filtered metrics; failures; model cards; and tests | RGB pixels are state-rendered and filters see full rules; physics is planar contact replay, not physical-camera, mobile-robot-controller, ROS, or hardware evidence. |
| 3 | `projects/constraint-aware-massing-explorer` | hard constraints, proxy objectives, Pareto ranking, baseline evaluation, diagrams, and tests | Rectangular proxy geometry; not professional design. |

The specification and QS projects extend the same AEC workflow with auditability and commercial-review boundaries. The specification assistant also publishes a separate candidate-authored direct/paraphrase/negative language stress audit instead of relying only on its perfect grammar regression. Their [cross-project integration](../integrations/aec-design-to-cost/README.md) is executable and tested; it is not counted as a sixth selected project. Eight focused baselines and workflow studies remain under [`experiments/`](../experiments/README.md).

## Fast Verification

```bash
python scripts/reviewer_check.py
```

The command validates the public documentation and runs selected-work tests without rewriting tracked artifacts. Full repository regeneration, formatting, linting, and test verification remains `python scripts/verify.py`.

The [evidence ledger](EVIDENCE_LEDGER.md) maps displayed metrics to versioned artifacts, evaluation scope, and reproduction commands.

## Role-Specific Evidence

- Applied AEC AI: AEC RAG, Massing Explorer, Communication and Specification Assistant, then QS Workbench.
- Embodied AI and robotics: Construction Embodied Agent, Grid Route Planner, then Robot Telemetry Monitor.
- Retrieval and LLM systems: AEC RAG, Communication and Specification Assistant state machine, then the deterministic research-workflow experiment.
- ML and MLOps: the text-classification and model-monitoring experiments retain focused classical-model evidence but are not selected work.

## Technical Questions Supported By Evidence

- How does page and authority metadata move from public AEC documents into citations?
- Why is document Hit@1 `0.952` while exact-target Hit@1 is `0.810`, and how are target IDs validated against the indexed corpus?
- Why compare lexical, probabilistic, latent-semantic, and hybrid retrieval locally?
- Why is hybrid-versus-BM25 inconclusive despite a higher MRR point estimate, and what would narrow the no-answer interval?
- How do raw and filtered policies differ in discrete rollouts and planar contact replay, and what does the unseen RGB palette reveal about visual brittleness?
- How are hard massing constraints separated from editable proxy objectives?
- How do message ids, requirement versions, approval scopes, and draft clauses remain traceable?
- How are shared walls deduplicated, rate units validated, and tender exceptions explained?
- Which approved requirements cross the integration boundary, which remain under human review, and which invalid handoffs fail closed?

## Ownership Check

High-signal ownership evidence is a live change to retrieval behavior, a new embodied or massing scenario with a regression test, or a modified integration fixture followed by a correct explanation of changed sources, outputs, and rejections. README fluency alone is not ownership evidence.
