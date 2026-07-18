# Authenticity And Ownership

This repository is intentionally local-first. That choice keeps the core workflows inspectable without private data, paid APIs, or cloud accounts.

## Engineering Decisions

- Synthetic data is used because real AEC, customer, and robot-site data would create privacy and professional-liability issues.
- Mock LLM/VLM providers exist so tests can exercise workflow behavior without paid services.
- AEC RAG is the primary project because it best connects the candidate's built-environment background with applied AI engineering.
- TF-IDF was kept because it is transparent and fast. BM25, dense LSA, and hybrid retrieval were added to compare local baselines without pretending to use hosted neural retrieval.
- Agent planning is deterministic by default so tool selection, retries, citations, and approval checkpoints can be tested.
- MLOps uses synthetic churn data to show schema validation, artifact metadata, logging, and drift simulation without claiming production monitoring.

## Known Tradeoffs

- Synthetic evals are useful for regression and review, not real benchmark evidence.
- Citation coverage is lexical and deterministic; it is not full factual verification.
- The agent is a traceable local workflow, not autonomous web research.
- The MLOps project is a local skeleton, not a deployed platform.
- VLM mock mode validates schemas and product boundaries, not visual intelligence.

## Evidence Not Claimed

- No public demo video is used as evidence in the repository.
- The included screenshots come from local runs and do not establish deployment.
- The public AEC corpus is downloaded locally and remains too small for a real compliance benchmark.
- Hosted-provider quality is not claimed where only deterministic mock mode is tested.
- The vision threshold baseline and VLM workflow are tiered as experiments, not trained deep-learning evidence.
