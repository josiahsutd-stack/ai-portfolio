# Technical Review Guide

The selected set contains one flagship, two role-defining primary projects, and two supporting AEC workflow systems. Fourteen narrower baselines remain under `experiments/`.

## 1. AEC Code Compliance RAG - Flagship

**Implemented:** fail-closed public downloads, corpus fingerprints, page and section metadata, unique chunk IDs, source filters, TF-IDF/BM25/dense-LSA/hybrid retrieval, citation objects, status handling, document/exact-chunk/source-page evaluation, target-label validation and audit, fixed-case confidence intervals, paired mode comparisons, failure analysis, and a fail-closed local API with request tracing, redacted audit logs, readiness, bounded durable telemetry, and query latency/error objectives.

**Evidence:** `src/aec_code_compliance_rag/`, `scripts/evaluate_retrieval.py`, `evaluate_service.py`, `evaluate_service_reliability.py`, `EVAL.md`, `ARCHITECTURE.md`, `demo_outputs/`, `tests/test_rag.py`, and `tests/test_rag_service.py`.

**Technical question:** How does provenance move from a downloaded document into a cited answer, and when does the system abstain?

**Boundary:** The 51-case default set is synthetic. The 24-case public result describes one fingerprinted 15-document snapshot, not current-code validation or professional compliance advice. Its 21 chunk targets and 18 page targets are candidate-authored, not independent expert labels. Document Hit@1 is `0.952`, exact-target Hit@1 is `0.810`, and page-target Hit@1 is `0.778`. Intervals resample the same cases and do not establish external validity; no-answer is only 2/2. The service suites are in-process ASGI evidence, not external deployment, sustained capacity, uptime, security-assessment, or usage evidence.

## 2. Construction Embodied Agent Simulator - Primary

**Implemented:** language-to-task parsing, procedural train/holdout grids, shared expert A* demonstrations, engineered-state random-forest imitation, world-raster and egocentric-state MLPs, a rendered-RGB MLP with an unseen appearance shift, raw and filtered rollouts, intervention logs, closed-loop metrics, failure analysis, and a planar MuJoCo command/contact replay.

**Evidence:** `environment.py`, `policies.py`, `learning.py`, `physics_replay.py`, `EVAL.md`, `demo_outputs/behavior_cloning_failure_analysis.md`, `demo_outputs/physics_replay_summary.json`, and `tests/test_vla_embodied_agent.py`.

**Technical question:** Why does agent-centered encoding recover the world-raster MLP's performance, why does the RGB policy collapse under an unseen palette, how does filtering change planar contact outcomes, and which physical risks remain absent?

**Boundary:** Semantic values and RGB pixels originate from simulator state. Local classifiers hide off-window hazards but retain relative subgoal geometry, and their filters apply full-state rules. MuJoCo replays planar targets against static proxies; this is not physical-camera perception, a foundation VLA, a mobile-robot controller, ROS, or hardware validation.

## 3. Constraint-Aware Massing Explorer - Primary

**Implemented:** four rectangular typologies, hard site/height/coverage/GFA/access checks, proxy objectives, Pareto filtering, weighted ranking, naive baseline comparison, seeded evaluation, SVG plans and isometrics, and focused tests.

**Evidence:** `generator.py`, `constraints.py`, `objectives.py`, `evaluation.py`, `EVAL.md`, `demo_outputs/`, and `tests/test_massing_explorer.py`.

**Technical question:** Which constraints fail closed, how are Pareto options selected, and where do environmental proxies stop being trustworthy?

**Boundary:** No code inference, internal egress model, calibrated daylight/CFD, structure, constructability, or approvable design.

## 4. Project Brief and Specification Copilot - Supporting

**Implemented:** immutable role-tagged messages, requirement versions, conflict records, approval scopes, SQLite audit events, source ids, open decisions, and clauses generated only from approved requirements.

**Evidence:** `engine.py`, `extractor.py`, `store.py`, `EVAL.md`, `demo_outputs/sample_specification.md`, and `tests/test_project_specification_copilot.py`.

**Boundary:** Perfect fixture metrics are regression results over an authored deterministic grammar, not open-domain language understanding or a professional specification.

## 5. QS Takeoff and Tender Analysis Workbench - Supporting

**Implemented:** typed vector plans, shared-wall segmentation, opening deductions, seven quantity classes, unit-safe rates, provenance, uncertainty bands, tender completeness and ratio checks, visual outputs, and focused tests.

**Evidence:** `takeoff.py`, `costing.py`, `tender.py`, `EVAL.md`, `demo_outputs/`, and `tests/test_qs_takeoff_tender_analysis.py`.

**Boundary:** No PDF/CAD/BIM extraction, current market rates, bill of quantities, professional QS validation, or award recommendation.

## Cross-Project Contract

The [AEC design-to-cost integration](../integrations/aec-design-to-cost/README.md) executes a source-linked handoff across projects rather than implying interoperability from a diagram. It maps three approved requirements, retains two approved requirements for human review, validates site-area and height invariants, selects a feasible storey-matched candidate, and passes its ground-floor mass footprints into the typed QS interface.

**Evidence:** `integrations/aec-design-to-cost/run_workflow.py`, `demo_outputs/workflow_trace.json`, `ARCHITECTURE.md`, and `tests/test_aec_workflow_integration.py`.

**Boundary:** This is one synthetic fixture and a contract regression. It is not evidence of end-to-end professional design, compliance, cost accuracy, or project delivery.

## Experiments And Baselines

The [`experiments/`](../experiments/README.md) directory contains generic model, workflow, MLOps, vision, ranking, time-series, BIM, energy, and smaller robotics studies. Their limitations are part of the public record; none carries equal depth to the flagship.

## Verification

```bash
python scripts/verify.py
```

The verifier scans claims and links, imports every module, regenerates deterministic artifacts twice, checks formatting and linting, and runs the complete test suite.
