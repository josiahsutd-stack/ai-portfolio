# Portfolio Review Rounds

## Round 0 - Baseline Audit

- Hiring-manager score: 6.5 / 10
- Major weaknesses found: too many projects compete for attention; AEC is strong but other flagships lack artifacts; root README needed clearer 15/60-minute review path; fine-tuning and VLM risk being overread if mock boundaries are missed.
- External benchmark insights: strong repos emphasize reproducible commands, architecture, evals, demo evidence, limitations, and fewer flagship systems.
- Research/industry insights: RAG and agent projects should expose evaluation and traceability; MLOps should include model metadata and drift/report artifacts; fine-tuning should not claim model improvement without training.
- Changes made: created `PORTFOLIO_BASELINE_AUDIT.md`.
- Tests run: local inspection and existing repo structure audit.
- Remaining weaknesses: supporting projects needed docs/demo outputs and root README still needed overhaul.
- Next priorities: benchmark externally, add research notes, then apply concrete changes.

## Round 1 - External Benchmarking

- Hiring-manager score: 6.8 / 10
- Major weaknesses found: repo had breadth but less project-specific evidence than strong public examples.
- External benchmark insights: Made With ML, Full Stack Deep Learning, MLOps Zoomcamp, ZenML examples, GraphRAG, PEFT, LLaVA, and MLflow docs all reinforce evidence-first project presentation.
- Research/industry insights: no code changes yet; focus was comparison.
- Changes made: created `EXTERNAL_PORTFOLIO_BENCHMARK.md`.
- Tests run: not applicable beyond source review.
- Remaining weaknesses: root README and supporting projects needed implementation/docs updates.
- Next priorities: add research notes and translate them into local, testable upgrades.

## Round 2 - Research Scan

- Hiring-manager score: 7.0 / 10
- Major weaknesses found: AEC eval needed MRR/no-answer/failure metrics; MLOps drift was too simple; fine-tuning validation was too permissive; VLM prompt contract was implicit.
- External benchmark insights: avoid copying; adapt only repeatable patterns.
- Research/industry insights: RAGAS-style component metrics, ReAct-style traces, MLflow-style metadata, Evidently-style drift, PEFT/LoRA honesty, VLM benchmark caution.
- Changes made: created `SOTA_RESEARCH_NOTES.md` as research notes, not SOTA claims.
- Tests run: not applicable yet.
- Remaining weaknesses: code and docs still needed to reflect these insights.
- Next priorities: implement lightweight improvements without adding heavy dependencies.

## Round 3 - Positioning And Flagship Depth

- Hiring-manager score: 7.4 / 10
- Major weaknesses found: root README needed a clearer five-project review path and explicit "what not to infer" section.
- External benchmark insights: first page should route reviewers, not list everything equally.
- Research/industry insights: mock/synthetic boundaries are part of system trust.
- Changes made: overhauled `README.md`; expanded AEC eval metrics; added AEC script wrapper and failure output.
- Tests run: pending full validation.
- Remaining weaknesses: supporting projects still needed architecture docs/demo outputs.
- Next priorities: update agent, MLOps, fine-tuning, and VLM artifacts.

## Round 4 - Supporting Review-Project Upgrade

- Hiring-manager score at the time: 7.8 / 10
- Major weaknesses found: agent/MLOps/fine-tuning/VLM had runnable code but not enough reviewer-facing artifacts.
- External benchmark insights: strong projects show architecture, output samples, and limitations close to the code.
- Research/industry insights: MLOps metadata and drift reports, agent traces, LoRA dataset validation, and VLM prompt contracts are credible lightweight improvements.
- Changes made: added project docs/demo outputs; improved MLOps metadata/logging/drift/report code; improved fine-tuning validation/eval template; added VLM prompt builder.
- Tests run: pending full validation.
- Remaining weaknesses: no screenshots or live deployment evidence.
- Next priorities: run validation and write final review.

## Round 5 - Final Review And Validation

- Hiring-manager score at the time: 8.0 / 10 for junior/applied roles
- Major weaknesses found: still not senior-level evidence; production claims remain intentionally limited.
- External benchmark insights: repo now better matches the evidence pattern of strong public portfolios while staying original.
- Research/industry insights: incorporated only local/testable ideas.
- Changes made: created `FINAL_HIRING_MANAGER_REVIEW.md`; ran repo-wide validation.
- Tests run: see final assistant summary for exact commands and results.
- Remaining weaknesses: no real users, no real production deployment, no real fine-tuning/VLM/AEC compliance benchmark.
- Next priorities: add screenshots, expand AEC corpus/eval, and add real hosted-provider demos where appropriate.

## Round 6 - Skeptical Second-Pass Review

- Hiring-manager score after correction: 7.4 / 10 for junior/applied roles; 4.5 / 10 for senior AI engineering.
- Major weaknesses found: too many projects were still labeled as flagship; the final score was too generous for a synthetic/local portfolio; some docs used production-adjacent wording such as "deployed endpoint" or "deployed demos"; the research notes could be misread as implemented capability; the AEC eval doc had a stale direct-script command alongside the wrapper command.
- Credibility fixes made: AEC is now the only project marked `flagship: true` in `projects/projects.yml`; agent, MLOps, fine-tuning, and VLM are described as supporting review projects; README language now says "evidence to inspect" and "demonstrates" rather than "proves"; research notes are retitled as not-SOTA claims; stale AEC eval command was removed.
- Tests added: MLOps artifact metadata is checked for feature schema, dataset info, and git commit field; fine-tuning split logic is checked for invalid train ratios.
- Projects moved down in reviewer priority: VLA Embodied Agent Simulator and Reinforcement Learning Portfolio remain experimental; the supporting AI projects are no longer presented as co-flagships.
- Remaining weaknesses: no real users, no deployment screenshots/video, no real hosted VLM eval, no real LoRA run, no real AEC/legal corpus, no hardware robotics evidence.
- Next priorities: add visual proof of demos running, expand AEC corpus/evaluation before deepening other projects, and only raise the score after real external evidence or larger eval artifacts exist.

## Round 7 - Final Recruiter Screen

- Hiring-manager score after recruiter-screen polish: 7.6 / 10 for junior/applied roles; 4.5 / 10 for senior AI engineering.
- Major weaknesses found: the README was honest but still required a rushed recruiter to piece together the verdict, top projects, proof artifacts, commands, and boundaries from several sections.
- Changes made: added a first-screen `15-Minute Recruiter Screen` to `README.md`; made the top 3 projects explicit; added quick evidence commands, proof artifacts, and hard synthetic/mock boundaries near the top; updated the review guide and final hiring-manager review.
- Tests/checks added: `scripts/check_repo_health.py` now enforces the root README recruiter-screen structure so the repo cannot drift back to a vague first page without failing local verification.
- Remaining weaknesses: screenshots/video proof, real usage evidence, larger AEC eval corpus, hosted VLM evidence, real LoRA training, and hardware robotics evidence are still missing.
- Final interview verdict: interview for junior/applied AI and AI solutions roles; reject for senior production AI, production compliance-AI ownership, or robotics hardware roles based on this repo alone.

## Round 8 - Repo-Wide Recruiter-Proofing

- Hiring-manager score after full repo cleanup: 7.8 / 10 for junior/applied roles; 4.6 / 10 for senior AI engineering.
- Major weaknesses found: recurring self-facing headings in project READMEs; stale AEC docs that still described plain TF-IDF retrieval; missing repo-level claim scanner; review artifacts existed for the flagship but not enough generated evidence for the supporting agent and MLOps projects.
- Credibility fixes made: replaced self-facing README headings with `Reviewer Signal` and `Deployment-Relevant Extensions`; updated AEC docs to match hybrid TF-IDF/BM25 retrieval, metadata, abstention statuses, and citation checks; added claim policy, reviewer guide, ownership note, depth scorecard, ADRs, and artifact-generation automation.
- Evidence added: 50-case synthetic AEC eval, generated AEC failure/sample-answer outputs, agent trace eval outputs, MLOps eval/drift outputs, and a `scripts/generate_review_artifacts.py` command for reviewers.
- Tests and checks run: `python scripts/verify.py` passed; full pytest passed with 49 tests; claim scan passed for 72 markdown files; repo health passed for 18 projects; smoke tests passed for 18 importable project modules; ruff and black checks passed.
- Remaining weaknesses: no real users, no production deployment evidence, no real AEC/legal corpus, no hosted VLM evaluation, no real LoRA training run, no screenshots/video proof, and no hardware robotics deployment evidence.
- Final interview verdict: stronger junior/applied AI interview signal, especially for RAG plus domain-AI roles; still not enough evidence for senior production AI, production compliance ownership, or robotics hardware roles.
