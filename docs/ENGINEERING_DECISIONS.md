# Engineering Decisions And Evidence Boundaries

This repository is intentionally local-first. That choice keeps the core workflows inspectable without private data, paid APIs, or cloud accounts. The decisions below explain why each system uses its current data, model, and integration boundary.

## Engineering Decisions

- Synthetic data is used because real AEC, customer, and robot-site data would create privacy and professional-liability issues.
- Mock LLM and visual-provider paths exist so tests can exercise workflow behavior without paid services.
- I selected AEC RAG as the primary project because it connects my built-environment background with applied AI engineering.
- I promoted the massing, specification, and QS systems only after each had focused tests, an evaluator, generated evidence, and explicit limitations.
- TF-IDF was kept because it is transparent and fast. BM25, dense LSA, and hybrid retrieval were added to compare local baselines without pretending to use hosted neural retrieval.
- Massing objectives remain transparent proxies because calibrated daylight, wind, structure, and egress simulation are not implemented.
- QS rates and tenders remain synthetic because current commercial data requires permission, provenance, and professional review.
- The AEC workflow is implemented as a separate tested adapter so project interoperability is demonstrated by a trace and rejection tests rather than implied by a diagram.
- Budget and accessibility remain outside automated geometry and costing because the current contracts cannot support a credible professional mapping.

## Known Tradeoffs

- Synthetic evals are useful for regression and review, not real benchmark evidence.
- Citation coverage is lexical and deterministic; it is not full factual verification.
- The specification extractor is a traceable deterministic grammar, not open-domain conversation intelligence.
- The QS workbench measures explicit vector fixtures, not arbitrary drawings.
- The integration converts mass footprints into room-like rectangles only to test typed data exchange; it does not claim that the resulting geometry is a functional plan.
- The visual-contract mock validates bytes and schemas while returning zero confidence and empty semantic fields.
- Supporting experiment names describe their executed mechanism: A* grid routing, telemetry rules, a deterministic research workflow, local model serving, and local artifact files. Broader robotics, autonomous-agent, registry, or platform behavior is not implied by their slugs.

## Evidence Not Claimed

- No public demo video is used as evidence in the repository.
- The included screenshots come from local runs and do not establish deployment.
- The public AEC corpus is downloaded locally and remains too small for a real compliance benchmark.
- Hosted-provider quality is not claimed where only deterministic mock mode is tested.
- The visual-provider contract is tiered as an experiment and does not count as trained visual-model evidence.
- The integration trace is one deterministic synthetic case, not a real project, customer workflow, or outcome.
