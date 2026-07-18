# Technical Review Guide

The selected set contains one flagship, two role-defining primary projects, and two supporting AEC workflow systems. Fourteen narrower baselines remain under `experiments/`.

## 1. AEC Code Compliance RAG - Flagship

**Implemented:** fail-closed public downloads, corpus fingerprints, page and section metadata, source filters, TF-IDF/BM25/dense-LSA/hybrid retrieval, citation objects, status handling, ablation, failure analysis, demo answers, and focused tests.

**Evidence:** `src/aec_code_compliance_rag/`, `scripts/evaluate_retrieval.py`, `EVAL.md`, `ARCHITECTURE.md`, `demo_outputs/`, and `tests/test_rag.py`.

**Technical question:** How does provenance move from a downloaded document into a cited answer, and when does the system abstain?

**Boundary:** The 51-case default set is synthetic. The 24-case public result describes one fingerprinted 15-document snapshot, not current-code validation or professional compliance advice.

## 2. Construction Embodied Agent Simulator - Primary

**Implemented:** language-to-task parsing, procedural train/holdout grids, shared expert A* demonstrations, engineered-state random-forest imitation, world-raster MLP imitation, egocentric 5x5 local-state MLP imitation, raw and filtered rollouts, intervention logs, closed-loop metrics, failure analysis, and replay traces.

**Evidence:** `environment.py`, `policies.py`, `learning.py`, `EVAL.md`, `demo_outputs/behavior_cloning_failure_analysis.md`, and `tests/test_vla_embodied_agent.py`.

**Technical question:** Why does agent-centered local encoding recover the world-raster MLP's performance, what information does its full-state filter add, and which physical risks remain absent?

**Boundary:** All semantic values come from simulator state. The egocentric classifier hides off-window hazards but retains relative subgoal geometry, and its filter applies full-state rules. This is not camera perception, a foundation VLA, physics, ROS, or hardware validation.

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
