# Codex Upgrade Work Log

## Current Repo Diagnosis

The repository is organized and honest, but the breadth can look like a keyword portfolio if every project appears equally important. The strongest evidence should be concentrated in AEC RAG, Agentic Research Ops, and MLOps Model Serving Monitoring.

## Highest-Signal Gaps

- AEC needed stronger local retrieval than TF-IDF alone.
- AEC needed larger eval data and explicit status/abstention metrics.
- Agent traces needed clearer retry/error and planner-rationale evidence.
- MLOps needed stricter prediction schema validation and generated eval artifacts.
- Repo-wide claims needed a policy and automated check.

## Implementation Checklist

- Add hybrid TF-IDF/BM25 retrieval and citation checks for AEC.
- Add 51 synthetic AEC eval cases and multiple synthetic documents, including a PDF-backed case.
- Add agent retry/error trace fields and eval artifact generation.
- Add MLOps schema validation, richer metrics, and eval artifact generation.
- Add claims policy, reviewer guide, authenticity note, depth scorecard, ADRs, and artifact-generation script.

## Files Changed

- Root reviewer surface: `README.md`, `FINAL_HIRING_MANAGER_REVIEW.md`, and `PORTFOLIO_REVIEW_ROUNDS.md`.
- Repo guardrails: `docs/CLAIMS_POLICY.md`, `docs/REVIEWER_GUIDE.md`, `docs/AUTHENTICITY_AND_OWNERSHIP.md`, `docs/PROJECT_DEPTH_SCORECARD.md`, `docs/DEMO_RECORDING_GUIDE.md`, and ADRs in `docs/adr/`.
- Automation: `scripts/check_claims.py`, `scripts/generate_review_artifacts.py`, `scripts/check_repo_health.py`, `scripts/verify.py`, and `Makefile`.
- AEC flagship: retrieval, chunk metadata, faithfulness checks, eval script, synthetic corpus, eval cases, limitations/system/case-study docs, and generated `demo_outputs/`.
- Agent support project: retry/error trace handling, denied-tool behavior, trace evaluation script, docs, and generated `demo_outputs/`.
- MLOps support project: Pydantic schema validation, richer model metadata, drift report fields, API health/model-info routes, eval script, docs, and generated `demo_outputs/`.
- Repo-wide README wording: self-facing headings were replaced with reviewer-facing `Reviewer Signal` and `Deployment-Relevant Extensions` headings.

## Tests Added

- AEC BM25, dense LSA, hybrid retrieval, ablation, and citation faithfulness tests.
- AEC unsupported-scope/no-evidence tests.
- Agent retry success, retry exhaustion, and denied-tool tests.
- MLOps invalid payload and schema validation tests.

## Commands Run

- `python scripts/check_claims.py` - passed in the last recorded full verification run.
- `python scripts/check_repo_health.py` - passed for 18 projects.
- `python scripts/run_smoke_tests.py` - passed for 18 importable project modules.
- `python -m pytest -q` - 49 passed.
- `python -m ruff check .` - passed.
- `python -m black --check .` - passed.
- `python scripts/verify.py` - passed end-to-end, including sample data generation, repo health, claims scan, smoke tests, review artifact generation, black, ruff, and pytest.

## Generated Evidence Snapshot

- AEC synthetic eval: 51 cases, recall@4 `0.922`, retrieval hit@3 `1.0`, status accuracy `1.0`, citation-check pass rate `1.0`.
- Agent eval: 6 tasks, approval gate rate `1.0`, unsupported/no-evidence/tool-error handling passed.
- MLOps eval: schema validation and drift report artifacts generated; perfect classification metrics are from deterministic synthetic churn data and should not be read as real-world model quality.

## Remaining Honest Limitations

- No real users or customer data.
- No production deployment evidence.
- No legal/code/compliance validation.
- No real robot hardware deployment.
- No real LoRA training run.
- VLM mock mode remains workflow validation, not visual reasoning.
