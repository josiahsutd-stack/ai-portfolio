# Evidence Coverage Audit

**Scope:** repository evidence inventory dated 18 July 2026. This document records what the code and versioned artifacts demonstrate and what remains unproven. It is not an external review, professional validation, or hiring recommendation.

## Coverage Matrix

| Area | Implemented evidence | Source of record | Not demonstrated |
| --- | --- | --- | --- |
| AEC document retrieval | Validated public-document ingestion, metadata-rich chunks, four local retrieval modes, citations, abstention, adversarial cases, ablation, and failure analysis. | [AEC RAG evaluation](projects/aec-code-compliance-rag/EVAL.md) and [public-source inventory](projects/aec-code-compliance-rag/public_sources/SOURCE_NOTES.md) | Compliance certification, legal advice, authority approval, or a broad expert-labeled benchmark. |
| Embodied-agent control | Three observation representations trained from shared A* demonstrations; disjoint holdout action metrics; raw and filtered rollouts; intervention counts; terminal-semantics regression tests. | [Embodied evaluation](projects/vla-embodied-agent-simulator/EVAL.md) and [model cards](projects/vla-embodied-agent-simulator/demo_outputs/) | Camera perception, foundation VLA behavior, physics, ROS 2 integration, robot hardware, or physical-safety validation. |
| Constraint-aware massing | Parametric geometry, hard-constraint filtering, editable objective proxies, Pareto ranking, unconstrained baseline, and generated option diagrams. | [Massing evaluation](projects/constraint-aware-massing-explorer/EVAL.md) | Code inference, internal egress, structure, calibrated daylight or CFD, and approvable design output. |
| Project requirements | Role-tagged messages, versioned requirements, conflicts, scoped approvals, source ids, audit events, and draft clauses over authored fixtures. | [Specification evaluation](projects/project-specification-copilot/EVAL.md) | Open-domain conversation understanding, uncontrolled natural language, professional specification authorship, or live-team usage. |
| Quantity and tender analysis | Shared-wall geometry, opening deductions, quantity formulas, rate provenance, uncertainty bands, and line-level tender exceptions. | [QS evaluation](projects/qs-takeoff-tender-analysis/EVAL.md) | PDF, CAD, or BIM extraction; current market rates; professional QS validation; or award recommendation. |
| Cross-project workflow | Executable typed handoff from approved requirements to sourced massing inputs and a bounded schematic takeoff, including rejection tests and a generated trace. | [AEC integration evidence](integrations/aec-design-to-cost/EVAL.md) | A complete design process, budget compliance, accessibility resolution, tender execution, or real-project interoperability. |
| Repository reproducibility | Local setup, focused evaluators, checked-in artifacts, claim checks, link checks, import smoke tests, formatting, linting, pytest, and artifact-idempotence checks. | [Verification script](scripts/verify.py) and [evidence ledger](docs/EVIDENCE_LEDGER.md) | Cloud reliability, authenticated deployment, service-level objectives, user telemetry, or customer adoption. |

## Review Paths

- The [five- and fifteen-minute paths](docs/how-to-review-this-portfolio.md) identify the shortest evidence sequence.
- The [evidence ledger](docs/EVIDENCE_LEDGER.md) maps quantitative claims to JSON artifacts and reproduction commands.
- The [claims policy](docs/CLAIMS_POLICY.md) defines language that is allowed or rejected.
- The [scope and limitations](docs/SCOPE_AND_LIMITATIONS.md) collects cross-project boundaries.
- The [engineering review history](PORTFOLIO_REVIEW_ROUNDS.md) records defects and corrective changes.

## Evidence Gaps

The repository does not claim to close these gaps:

1. Independent labels or review from an architect, engineer, quantity surveyor, authority, robotics practitioner, or other domain professional.
2. Permissioned real-project data with a held-out protocol and documented annotation disagreements.
3. A deployed selected project with authentication, monitoring, latency and error objectives, and usage evidence.
4. An embodied-policy input derived from sensed data, a physics-based simulator, ROS 2, or hardware.
5. Evidence of customer use, operational reliability, professional acceptance, or commercial outcomes.

## Highest-Value Next Evidence

1. One permissioned public or partner AEC dataset with expert labels and a held-out evaluation protocol.
2. One deployed selected project with authentication, monitoring, latency/error budgets, and usage evidence.
3. One robotics integration beyond synthetic semantic state, such as perception input, ROS 2 simulation, or a physics-based environment.
4. Professional review of a bounded massing, specification, or QS output with documented disagreement and corrections.
