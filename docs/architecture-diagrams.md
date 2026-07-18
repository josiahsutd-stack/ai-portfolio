# System Maps

The portfolio uses diagrams to expose implemented boundaries, not to imply integrations that do not exist. Detailed component maps remain beside each selected project's code. The cross-project map below is generated from an executed synthetic trace and is the only diagram that claims a handoff between projects.

## Executed AEC Journey

[![Executed AEC system journey with input streams, approval and source gates, typed project handoffs, traceability, and professional review](../integrations/aec-design-to-cost/demo_outputs/workflow_trace.svg)](../integrations/aec-design-to-cost/demo_outputs/workflow_trace.svg)

The trace connects two explicit inputs to three implemented systems:

1. Role-tagged project messages become versioned, role-approved requirements.
2. Approved requirements and supplied site fields form a source-linked massing scenario.
3. A feasible, storey-matched option becomes one schematic ground-floor envelope.
4. The envelope becomes a vector takeoff with synthetic rate provenance.
5. Budget, accessibility intent, professional design, full-project costing, and tender review remain outside automation.

The corresponding [`workflow_trace.json`](../integrations/aec-design-to-cost/demo_outputs/workflow_trace.json) retains message, requirement, site, candidate, and quantity identifiers. Rejection tests cover unapproved requirements, unresolved conflicts, invalid source invariants, missing eligible options, and candidate-provenance loss.

## Selected-System Maps

| System | Architectural question | Detailed map | Visual evidence |
| --- | --- | --- | --- |
| AEC Code Compliance RAG | How do source identity, page metadata, retrieval modes, citations, abstention, service controls, and telemetry remain separable? | [Architecture](../projects/aec-code-compliance-rag/ARCHITECTURE.md) | [Retrieval granularity](../projects/aec-code-compliance-rag/demo_outputs/public_sources/retrieval_granularity_comparison.svg) |
| Construction Embodied Agent Simulator | How are demonstrations, observation families, learned policies, action filtering, discrete rollouts, and planar contact replay compared without conflating them? | [Architecture](../projects/vla-embodied-agent-simulator/ARCHITECTURE.md) | [Observation and policy comparison](../projects/vla-embodied-agent-simulator/demo_outputs/semantic_raster_comparison.svg) |
| Constraint-Aware Massing Explorer | Where are supplied constraints, seeded generators, feasibility checks, proxy objectives, Pareto ranking, and generated geometry separated? | [Architecture](../projects/constraint-aware-massing-explorer/ARCHITECTURE.md) | [Evaluated option comparison](../projects/constraint-aware-massing-explorer/demo_outputs/option_comparison.svg) |
| Project Communication and Specification Assistant | How do messages, requirement versions, conflicts, approval scopes, source links, draft clauses, and audit events remain traceable? | [Architecture](../projects/project-specification-copilot/ARCHITECTURE.md) | [Generated requirement trace](../projects/project-specification-copilot/demo_outputs/sample_trace.svg) |
| QS Takeoff and Tender Analysis Workbench | How do validated geometry, shared-wall measurement, quantity formulas, rate provenance, uncertainty, and tender exceptions remain inspectable? | [Architecture](../projects/qs-takeoff-tender-analysis/ARCHITECTURE.md) | [Measured vector plan](../projects/qs-takeoff-tender-analysis/demo_outputs/sample_plan.svg) |

## Diagram Policy

- Every quantitative diagram is generated from a versioned JSON artifact or evaluated geometry.
- Concept imagery is labeled separately and never presented as implementation evidence.
- Synthetic inputs, simulation-only behavior, and professional-review boundaries remain visible beside the diagram.
- Project-specific diagrams describe internal structure; only the executed integration trace claims a cross-project handoff.
