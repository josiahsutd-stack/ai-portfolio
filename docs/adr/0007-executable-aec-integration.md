# ADR 0007: Executable AEC Integration Over Conceptual Workflow Claims

**Status:** Accepted

## Context

The specification, massing, and QS projects had related domain narratives and independently runnable interfaces. A workflow diagram alone did not demonstrate that their schemas could exchange data or reject incompatible inputs.

## Decision

Maintain a separate `integrations/aec-design-to-cost/` contract that:

- accepts only approved, conflict-free requirements;
- records field-level sources for every massing input;
- checks cross-project area and height invariants;
- passes selected mass footprints into the typed QS interface under a narrow schematic scope;
- retains unsupported approved requirements for human review;
- generates deterministic artifacts and rejection-path tests.

The integration is not listed as another selected project and does not add model-quality claims.

## Consequences

The repository can point to executable interoperability evidence. The adapter also makes omissions visible: code inference, professional design, whole-building costing, budget comparison, and tender analysis remain outside the handoff.

## Alternatives Considered

Directly coupling the three project packages was rejected because it would blur ownership boundaries. A narrative-only diagram was rejected because it could overstate integration. Automatic budget comparison and tender generation were rejected because the available scopes and data do not support credible results.
