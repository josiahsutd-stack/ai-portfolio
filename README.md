# Applied AI Engineering Portfolio

Applied AI engineer focused on source-grounded LLM systems, agent workflows, local MLOps skeletons, multimodal product interfaces, and built-environment AI.

This repository is intentionally local-first: projects run with synthetic data or mock providers so reviewers can inspect engineering structure without private datasets, paid APIs, or hidden services.

## 15-Minute Recruiter Screen

Verdict: this repo can support a junior/applied AI engineering interview, especially for teams that value RAG, agent workflows, MLOps basics, and built-environment domain thinking. It should not be read as evidence of senior production ownership, real compliance validation, real robot deployment, or real customer adoption.

Top 3 reviewer targets:

1. [AEC Code Compliance RAG](projects/aec-code-compliance-rag/README.md) - primary project with retrieval evaluation, citations, architecture docs, demo outputs, and tests.
2. [Agentic Research Ops Assistant](projects/agentic-research-ops-assistant/README.md) - supporting agent workflow with tool traces, citations, approval checkpoints, SQLite persistence, and trace eval.
3. [MLOps Model Serving Monitoring](projects/mlops-model-serving-monitoring/README.md) - supporting MLOps workflow with model metadata, schema checks, prediction logs, drift reports, and monitoring docs.

Runnable verification commands:

```bash
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py
python -m pytest tests/test_rag.py tests/test_general_ai_projects.py
python scripts/generate_review_artifacts.py
```

Proof beyond claims:

- AEC eval and generated demo outputs: [EVAL.md](projects/aec-code-compliance-rag/EVAL.md), [demo_outputs/](projects/aec-code-compliance-rag/demo_outputs/)
- Architecture docs close to the code: [AEC ARCHITECTURE.md](projects/aec-code-compliance-rag/ARCHITECTURE.md), [technical review guide](docs/technical-review-guide.md)
- Test coverage for retrieval, citations, no-answer handling, agent traces, MLOps metadata, LoRA validation, and VLM prompt contracts.
- Self-review files that state the weaknesses plainly: [PORTFOLIO_REVIEW_ROUNDS.md](PORTFOLIO_REVIEW_ROUNDS.md), [FINAL_HIRING_MANAGER_REVIEW.md](FINAL_HIRING_MANAGER_REVIEW.md)
- Claim and ownership controls: [CLAIMS_POLICY.md](docs/CLAIMS_POLICY.md), [AUTHENTICITY_AND_OWNERSHIP.md](docs/AUTHENTICITY_AND_OWNERSHIP.md), [PROJECT_DEPTH_SCORECARD.md](docs/PROJECT_DEPTH_SCORECARD.md)

Hard boundaries: all datasets are synthetic unless stated otherwise; mock LLM/VLM paths test workflow behavior, not model intelligence; AEC outputs are not legal, code, engineering, architectural, or professional compliance advice.

## Highest-Signal Projects

| Project | Evidence to inspect | What is real | What is mocked or synthetic |
| --- | --- | --- | --- |
| [AEC Code Compliance RAG](projects/aec-code-compliance-rag/README.md) | Primary review project: RAG, citations, eval, and AEC domain fit. | Chunking, metadata, hybrid TF-IDF/BM25 retrieval, citation formatting, eval script, demo outputs, tests. | Synthetic guidance; markdown page markers; no legal/code advice. |
| [Agentic Research Ops Assistant](projects/agentic-research-ops-assistant/README.md) | Agent orchestration, tool registry, approval gate, traces. | Planner/executor flow, local search, tool traces, SQLite persistence, trace eval. | Local demo docs; deterministic tools; not autonomous web research. |
| [MLOps Model Serving Monitoring](projects/mlops-model-serving-monitoring/README.md) | Model lifecycle, serving schema, logging, drift report. | Training pipeline, artifact metadata, FastAPI-compatible functions, SQLite logs, PSI-style drift checks. | Synthetic churn data; local registry; no production alerting. |
| [Fine-Tuning LoRA Lab](projects/fine-tuning-lora-lab/README.md) | Honest adaptation workflow and dataset discipline. | Dataset generation, validation, split checks, LoRA config, eval template. | Training is mocked; no model weights are updated. |
| [Multimodal VLM Visual QA](projects/multimodal-vlm-visual-qa/README.md) | Multimodal product boundary and structured outputs. | Image validation, prompt contract, schema parsing, mock provider, optional OpenAI-compatible path. | Mock mode does not perform real visual reasoning. |

## Recruiter Evidence Map

For a short screen, the strongest evidence is concentrated in the primary AEC project, its evaluation docs, and one supporting system depending on role: agent workflows, MLOps, fine-tuning workflow, or VLM product boundary.

Key evidence files:

- Primary project: [projects/aec-code-compliance-rag](projects/aec-code-compliance-rag/README.md)
- AEC evaluation: [AEC EVAL.md](projects/aec-code-compliance-rag/EVAL.md)
- AEC architecture: [AEC ARCHITECTURE.md](projects/aec-code-compliance-rag/ARCHITECTURE.md)
- Focused tests: [tests/test_rag.py](tests/test_rag.py)
- Full local verification: `python scripts/verify.py`

## 15-Minute Verification Commands

```bash
python scripts/generate_sample_data.py
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py
python -m pytest tests/test_rag.py
streamlit run projects/aec-code-compliance-rag/app.py
```

Evidence produced by those commands:

- AEC citations and no-answer behavior.
- `demo_outputs/` artifacts for generated evidence.
- The root files `PORTFOLIO_BASELINE_AUDIT.md`, `PORTFOLIO_REVIEW_ROUNDS.md`, and `FINAL_HIRING_MANAGER_REVIEW.md`.

## 60-Minute Technical Verification

```bash
python scripts/verify.py
python -m pytest
python -m ruff check .
python -m black --check .
python scripts/check_repo_health.py
python scripts/run_smoke_tests.py
python scripts/check_project_docs.py
```

Code areas with the clearest signal:

- RAG: `projects/aec-code-compliance-rag/src/aec_code_compliance_rag/`
- Agent traces: `projects/agentic-research-ops-assistant/src/agentic_research_ops_assistant/`
- MLOps observability: `projects/mlops-model-serving-monitoring/src/mlops_model_serving_monitoring/`
- Fine-tuning workflow: `projects/fine-tuning-lora-lab/src/fine_tuning_lora_lab/workflow.py`
- VLM provider boundary: `projects/multimodal-vlm-visual-qa/src/multimodal_vlm_visual_qa/`

## What Is Implemented Versus Prototype

| Category | Meaning in this repo |
| --- | --- |
| Real implementation | Local code paths that run and are tested: retrieval, schema validation, mock providers, artifact writing, trace/log persistence, drift calculations. |
| Mock provider | Deterministic substitute for an LLM/VLM so the workflow can be tested without paid APIs. |
| Synthetic data | Generated/demo data with no customer, employer, or private project content. |
| Prototype | A runnable local skeleton that shows engineering shape but lacks production data, monitoring, security, and scale. |
| Local engineering scaffold | A small local version of a real concern, such as SQLite inference logs, model metadata, citation objects, trace records, eval cases, or drift reports. |

## Skills Demonstrated

- RAG: chunking, metadata, retrieval scoring, citations, evaluation, no-answer handling.
- LLM applications: provider abstraction, structured outputs, prompt contracts, uncertainty fields.
- Agents: planning, tool calls, approval gates, traces, persistence, trace evaluation.
- MLOps: training pipeline, model artifact metadata, inference logging, drift detection, monitoring report.
- Multimodal AI: image validation, VLM provider boundary, schema parsing, mock/hosted distinction.
- Fine-tuning workflow: dataset validation, LoRA config planning, eval templates, hardware honesty.
- Built-environment AI: AEC document-assistance workflow, BIM QA, construction robotics/safety simulations.

## Reproducibility

```bash
python scripts/setup.py
python scripts/verify.py
```

`scripts/setup.py` creates `.venv` using the correct Windows/macOS/Linux path. Current-environment installation is also available through `python scripts/setup.py --no-venv`.

## Testing

```bash
python -m black --check .
python -m ruff check .
python scripts/check_repo_health.py
python scripts/run_smoke_tests.py
python -m pytest
python scripts/check_project_docs.py
```

The GitHub Actions workflow is present in `.github/workflows/ci.yml`. If GitHub does not run it because of an account billing lock, that is an account state issue, not a code/test result. Local verification is the source of truth here.

## Experiments And Supporting Projects

These broaden the portfolio but should not be treated as equally deep:

- Construction Progress CV Tracker
- BIM Issue Detection Agent
- AI + AEC Job Fit Analyzer
- Building Energy ML Pipeline
- Spatial Design Recommendation Engine
- Construction Robot Task Planner
- Site Robot Safety Monitor
- VLA Embodied Agent Simulator
- Reinforcement Learning Portfolio
- Deep Learning Vision Lab
- LLM Evals and Guardrails Platform
- Recommender System Ranking Engine
- Time-Series Anomaly Detection and Forecasting

## Honest Limitations

- No real users, customers, deployments, adoption, benchmark wins, or paid-client outcomes are claimed.
- All included datasets are synthetic unless a file explicitly says otherwise.
- Mock LLM/VLM paths validate workflow behavior, not model intelligence.
- AEC outputs are not legal, code, engineering, architectural, or professional compliance advice.
- Fine-tuning does not update real model weights locally.
- Robotics projects are simulations, not robot hardware deployments.
- CI may be blocked by GitHub account state even when local tests pass.

## What Not To Infer

- Do not infer production reliability from local demos.
- Do not infer real-world code-compliance capability from synthetic AEC examples.
- Do not infer real visual reasoning from mock VLM outputs.
- Do not infer real LoRA model improvement from the fine-tuning lab.
- Do not infer senior-level MLOps ownership from the local MLOps skeleton.

## Reviewer Docs

- [Baseline audit](PORTFOLIO_BASELINE_AUDIT.md)
- [Review rounds](PORTFOLIO_REVIEW_ROUNDS.md)
- [External portfolio benchmark](EXTERNAL_PORTFOLIO_BENCHMARK.md)
- [Research notes, not SOTA claims](SOTA_RESEARCH_NOTES.md)
- [Final hiring-manager review](FINAL_HIRING_MANAGER_REVIEW.md)
- [How to review this portfolio](docs/how-to-review-this-portfolio.md)
- [Technical review guide](docs/technical-review-guide.md)
- [Reviewer guide](docs/REVIEWER_GUIDE.md)
- [Claims policy](docs/CLAIMS_POLICY.md)
- [Authenticity and ownership](docs/AUTHENTICITY_AND_OWNERSHIP.md)
- [Project depth scorecard](docs/PROJECT_DEPTH_SCORECARD.md)
- [Upgrade work log](docs/CODEX_UPGRADE_PLAN.md)

## Portfolio Site

Portfolio site: [portfolio-site/index.html](portfolio-site/index.html)

Local static preview command:

```bash
python -m http.server 8080 --directory portfolio-site
```

## Contact

- GitHub: `https://github.com/josiahsutd-stack`
- LinkedIn: listed in application materials
- Email: listed in application materials
