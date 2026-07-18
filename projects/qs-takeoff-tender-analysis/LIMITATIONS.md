# Limitations and Human Review Boundary

## Input Coverage

- The bundled input is a rectangular, axis-aligned, single-storey JSON schema.
- The implementation does not read pixels, text, dimensions, symbols, layers, or revisions from PDF, image, CAD, BIM, or IFC files.
- Curves, angled walls, columns, shafts, stairs, roofs, multi-storey stacking, and non-room elements are unsupported.
- Room adjacency is inferred only from exact shared coordinates.

## Measurement Coverage

- Seven illustrative quantities are emitted; this is not a bill of quantities or standard method of measurement.
- Partition area is a one-face equivalent for the demo and must not be treated as a complete finishing or assembly measurement.
- Slab volume is a uniform thickness proxy with no beams, drops, reinforcement, waste, or formwork.
- No foundations, structure, MEP, external works, temporary works, logistics, preliminaries, testing, commissioning, or lifecycle cost is measured.

## Pricing Coverage

- Every bundled rate is synthetic and deliberately disconnected from current market data.
- The range applies a fixed item-level percentage; it is not a calibrated confidence interval.
- Currency conversion, escalation, location, specification quality, procurement route, quantity effects, taxes, overhead, profit, risk allowances, and contract conditions are excluded.

## Tender Coverage

- Tender comparison uses simple completeness and benchmark-ratio bands over normalized line-item codes.
- It does not parse tender documents, reconcile scopes, assess qualifications, detect collusion or fraud, score bidder capability, or recommend an award.
- Low prices can represent innovation, scope omission, error, or commercial strategy; high prices can represent scope differences or risk. Every flag requires clarification and professional review.

## Required Human Roles

A qualified quantity surveyor must validate measurement rules, quantities, rates, scope, assumptions, and commercial interpretation. Architects, engineers, clients, contractors, and legal advisers remain responsible for their respective design and contract decisions.
