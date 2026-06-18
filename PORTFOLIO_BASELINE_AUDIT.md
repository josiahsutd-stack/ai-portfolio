# Portfolio Baseline Audit

Audit date: 2026-06-19

Perspective: senior AI engineering hiring manager reviewing for junior/applied AI engineering roles.

## Summary Verdict

The portfolio is interviewable for junior/applied AI roles if reviewers start with the right projects. The AEC RAG project now has the clearest flagship signal. The rest of the repository still has uneven depth: many projects are runnable and honest, but several are closer to structured demos than deep systems. The strongest improvement path is not adding more projects; it is deepening the five named systems and making every claim traceable to code, tests, evals, or demo outputs.

## Scores

| Category | Score | Evidence | What would raise it | Problem type |
| --- | ---: | --- | --- | --- |
| Recruiter clarity | 7 | Root README points to AEC first and separates supporting projects. | Tighter 3-5 project framing across every doc and portfolio-site page. | Positioning/docs |
| Hiring-manager credibility | 7 | AEC has `EVAL.md`, `ARCHITECTURE.md`, demo outputs, and tests; MLOps and agent have real local persistence. | More project-specific architecture docs and failure outputs for agent, MLOps, fine-tuning, VLM. | Docs/testing |
| Technical depth | 6 | RAG, traces, drift checks, VLM schema parsing, and LoRA workflow exist. | Hybrid retrieval/reranking, richer agent failure handling, monitoring report generation, dataset leakage checks. | Architecture/code |
| Production realism | 5 | SQLite logs, model artifacts, Dockerfiles, CI workflow, and local smoke tests exist. | Versioned schemas, migrations, latency/error logging, monitoring thresholds, model rollback story. | Architecture/code |
| Testing quality | 7 | `python -m pytest` covers core behavior across projects. | More project-specific tests for scripts, generated artifacts, failure cases, and docs links. | Testing |
| Evaluation rigor | 5 | AEC retrieval eval exists; agent trace eval and LLM guardrail eval exist. | Answer-grounding checks, MRR/no-answer metrics, multimodal eval cases, LoRA held-out eval templates. | Evaluation |
| Code quality | 7 | Small modules, shared utilities, local-first design, Ruff/Black config. | Reduce repeated Streamlit bootstrapping and add more typed contracts for outputs. | Code |
| Documentation quality | 7 | READMEs include limitations and review notes. | Add root-level baseline/final reviews, external benchmark notes, and project-specific architecture docs. | Docs |
| Originality / differentiation | 8 | AEC plus construction robotics/built-environment angle is distinctive. | Make AEC RAG materially deeper than generic RAG demos. | Positioning/architecture |
| Interview conversion likelihood | 6 | Strong junior/applied signal if reviewer sees AEC first. | More screenshots/demo outputs and fewer equal-weight experiments in the first viewport. | Positioning/evidence |

## Major Weaknesses Found

- The repo still has many projects, which can dilute the hiring signal.
- Some supporting projects have credible code but thin project-specific artifacts.
- Fine-tuning is honest but too lightweight unless framed as a dataset/eval workflow rather than training.
- VLM mock mode can be misunderstood unless demo outputs and limitations are explicit.
- MLOps has useful local pieces but needs a clearer monitoring-report artifact and stronger drift metric explanation.
- Agent project needs architecture/limitations docs and example trace output for reviewers who do not run Streamlit.

## Baseline Evidence

- Root README: names AEC as the primary flagship and documents synthetic/mock limitations.
- AEC project: has retrieval eval, citation metadata, demo outputs, architecture docs, and focused tests.
- Agent project: has `AgentTrace`, `ToolCall`, SQLite trace store, permission-aware planning, and trace evaluation.
- MLOps project: has model training, artifact saving, SQLite logging, drift reports, Dockerfile, and tests.
- Fine-tuning project: has dataset generation, validation, split logic, and mock LoRA training.
- VLM project: has image validation, Pydantic schemas, mock provider, and OpenAI-compatible provider path.

## What Would Move This From Junior-Solid To Strong Applied-AI

1. Make AEC RAG visibly deeper than all other projects.
2. Add demo outputs and failure examples to every flagship/supporting project.
3. Expand evaluation beyond happy paths.
4. Keep mock and synthetic labels impossible to miss.
5. Use fewer first-page claims and more direct evidence links.
