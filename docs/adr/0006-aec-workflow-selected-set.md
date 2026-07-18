# ADR 0006: AEC Workflow Selected Set

## Context

The massing, specification, and QS projects now have focused tests, deterministic evaluators, generated evidence, architecture documentation, and explicit professional boundaries. The previous selected set over-emphasized generic model and MLOps breadth relative to the portfolio's AEC and embodied-AI specialization.

## Decision

Keep AEC Code Compliance RAG as the sole flagship. Select the Construction Embodied Agent Simulator and Constraint-Aware Massing Explorer as primary projects. Select the Project Brief and Specification Copilot and QS Takeoff and Tender Analysis Workbench as supporting AEC workflow projects.

Move the generic text-classification, research-workflow, and MLOps systems to `experiments/` while retaining their code, tests, and evidence.

## Consequences

- The first screen presents three differentiated projects with visible evaluation evidence.
- The selected set forms a coherent AEC workflow narrative; [ADR 0007](0007-executable-aec-integration.md) adds executable evidence for one bounded handoff without claiming full project delivery.
- Generic AI breadth remains available without appearing equivalent to the flagship.
- No promoted project claims production use, customer adoption, or professional sign-off.

## Promotion Gate

A project enters `projects/` only when it has a runnable local path, focused tests, an evaluation protocol, checked-in evidence, architecture documentation, and explicit limitations.
