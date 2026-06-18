# Portfolio Review Rounds

## Round 0 - Baseline Audit

- Hiring-manager score: 6.5 / 10
- Major weaknesses found: too many projects compete for attention; AEC is strong but other flagships lack artifacts; root README needed clearer 15/60-minute review path; fine-tuning and VLM risk being overread if mock boundaries are missed.
- External benchmark insights: strong repos emphasize reproducible commands, architecture, evals, demo evidence, limitations, and fewer flagship systems.
- SOTA/research insights: RAG and agent projects should expose evaluation and traceability; MLOps should include model metadata and drift/report artifacts; fine-tuning should not claim model improvement without training.
- Changes made: created `PORTFOLIO_BASELINE_AUDIT.md`.
- Tests run: local inspection and existing repo structure audit.
- Remaining weaknesses: supporting projects needed docs/demo outputs and root README still needed overhaul.
- Next priorities: benchmark externally, add research notes, then apply concrete changes.

## Round 1 - External Benchmarking

- Hiring-manager score: 6.8 / 10
- Major weaknesses found: repo had breadth but less project-specific evidence than strong public examples.
- External benchmark insights: Made With ML, Full Stack Deep Learning, MLOps Zoomcamp, ZenML examples, GraphRAG, PEFT, LLaVA, and MLflow docs all reinforce evidence-first project presentation.
- SOTA/research insights: no code changes yet; focus was comparison.
- Changes made: created `EXTERNAL_PORTFOLIO_BENCHMARK.md`.
- Tests run: not applicable beyond source review.
- Remaining weaknesses: root README and supporting projects needed implementation/docs updates.
- Next priorities: add SOTA notes and translate them into local, testable upgrades.

## Round 2 - SOTA / Research Scan

- Hiring-manager score: 7.0 / 10
- Major weaknesses found: AEC eval needed MRR/no-answer/failure metrics; MLOps drift was too simple; fine-tuning validation was too permissive; VLM prompt contract was implicit.
- External benchmark insights: avoid copying; adapt only repeatable patterns.
- SOTA/research insights: RAGAS-style component metrics, ReAct-style traces, MLflow-style metadata, Evidently-style drift, PEFT/LoRA honesty, VLM benchmark caution.
- Changes made: created `SOTA_RESEARCH_NOTES.md`.
- Tests run: not applicable yet.
- Remaining weaknesses: code and docs still needed to reflect these insights.
- Next priorities: implement lightweight improvements without adding heavy dependencies.

## Round 3 - Positioning And Flagship Depth

- Hiring-manager score: 7.4 / 10
- Major weaknesses found: root README needed a clearer five-project review path and explicit "what not to infer" section.
- External benchmark insights: first page should route reviewers, not list everything equally.
- SOTA/research insights: mock/synthetic boundaries are part of system trust.
- Changes made: overhauled `README.md`; expanded AEC eval metrics; added AEC script wrapper and failure output.
- Tests run: pending full validation.
- Remaining weaknesses: supporting projects still needed architecture docs/demo outputs.
- Next priorities: update agent, MLOps, fine-tuning, and VLM artifacts.

## Round 4 - Supporting Flagship Upgrade

- Hiring-manager score: 7.8 / 10
- Major weaknesses found: agent/MLOps/fine-tuning/VLM had runnable code but not enough reviewer-facing artifacts.
- External benchmark insights: strong projects show architecture, output samples, and limitations close to the code.
- SOTA/research insights: MLOps metadata and drift reports, agent traces, LoRA dataset validation, and VLM prompt contracts are credible lightweight improvements.
- Changes made: added project docs/demo outputs; improved MLOps metadata/logging/drift/report code; improved fine-tuning validation/eval template; added VLM prompt builder.
- Tests run: pending full validation.
- Remaining weaknesses: no screenshots or live deployment evidence.
- Next priorities: run validation and write final review.

## Round 5 - Final Review And Validation

- Hiring-manager score: 8.0 / 10 for junior/applied roles
- Major weaknesses found: still not senior-level evidence; production claims remain intentionally limited.
- External benchmark insights: repo now better matches the evidence pattern of strong public portfolios while staying original.
- SOTA/research insights: incorporated only local/testable ideas.
- Changes made: created `FINAL_HIRING_MANAGER_REVIEW.md`; ran repo-wide validation.
- Tests run: see final assistant summary for exact commands and results.
- Remaining weaknesses: no real users, no real production deployment, no real fine-tuning/VLM/AEC compliance benchmark.
- Next priorities: add screenshots, expand AEC corpus/eval, and add real hosted-provider demos where appropriate.
