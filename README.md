# Applied AI Engineering Portfolio

Applied AI engineer focused on source-grounded LLM systems, agent workflows, MLOps workflows, multimodal product interfaces, and built-environment AI.

This repository is intentionally local-first: projects run with synthetic data or mock providers so reviewers can inspect engineering structure without private datasets, paid APIs, or hidden services.

## Portfolio Highlights

This portfolio focuses on applied AI engineering work that is runnable locally and documented with tests, evaluation scripts, architecture notes, and sample outputs.

![Portfolio site screenshot](docs/assets/screenshots/portfolio-home.png)

| Project | What it demonstrates | Evidence |
| --- | --- | --- |
| [AEC Code Compliance RAG](projects/aec-code-compliance-rag/README.md) | Source-grounded retrieval, Singapore public-source ingestion, citation formatting, no-answer handling, and AEC domain translation. | [EVAL.md](projects/aec-code-compliance-rag/EVAL.md), [public source notes](projects/aec-code-compliance-rag/public_sources/SOURCE_NOTES.md), [demo outputs](projects/aec-code-compliance-rag/demo_outputs/), [tests](tests/test_rag.py) |
| [Agentic Research Ops Assistant](projects/agentic-research-ops-assistant/README.md) | Planner-executor workflow, tool traces, approval checkpoints, citations, and local persistence. | [ARCHITECTURE.md](projects/agentic-research-ops-assistant/ARCHITECTURE.md), [demo outputs](projects/agentic-research-ops-assistant/demo_outputs/), trace evaluation |
| [MLOps Model Serving Monitoring](projects/mlops-model-serving-monitoring/README.md) | Model metadata, schema validation, prediction logging, drift reporting, and monitoring docs. | [MODEL_CARD.md](projects/mlops-model-serving-monitoring/MODEL_CARD.md), [MONITORING.md](projects/mlops-model-serving-monitoring/MONITORING.md), [demo outputs](projects/mlops-model-serving-monitoring/demo_outputs/) |

The projects use synthetic data and mock providers where needed, so the repository can be reviewed without private datasets, paid APIs, or hidden services.

## Quick Verification

```bash
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py
python projects/aec-code-compliance-rag/scripts/download_public_sources.py
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py --corpus public
python -m pytest tests/test_rag.py tests/test_general_ai_projects.py
python projects/vla-embodied-agent-simulator/evaluate_vla.py
python scripts/generate_review_artifacts.py
python scripts/check_portfolio_site.py
```

## Technical Evidence

- AEC eval and generated demo outputs: [EVAL.md](projects/aec-code-compliance-rag/EVAL.md), [demo_outputs/](projects/aec-code-compliance-rag/demo_outputs/), [Singapore public-source notes](projects/aec-code-compliance-rag/public_sources/SOURCE_NOTES.md)
- Architecture docs close to the code: [AEC ARCHITECTURE.md](projects/aec-code-compliance-rag/ARCHITECTURE.md), [technical review guide](docs/technical-review-guide.md)
- Demo screenshots: [portfolio home](docs/assets/screenshots/portfolio-home.png), [AEC RAG app](docs/assets/screenshots/aec-rag-demo.png)
- VLA simulation outputs: [VLA README](projects/vla-embodied-agent-simulator/README.md), [policy evaluation artifacts](projects/vla-embodied-agent-simulator/demo_outputs/vla_eval_report.md), and [sample replay traces](projects/vla-embodied-agent-simulator/demo_outputs/sample_episode_replay.md).
- Test coverage for retrieval, citations, no-answer handling, agent traces, MLOps metadata, LoRA validation, VLM prompt contracts, and VLA action safety.
- Project scope and review docs: [CLAIMS_POLICY.md](docs/CLAIMS_POLICY.md), [AUTHENTICITY_AND_OWNERSHIP.md](docs/AUTHENTICITY_AND_OWNERSHIP.md), [REVIEWER_GUIDE.md](docs/REVIEWER_GUIDE.md)

## Scope

This is a local-first engineering portfolio. It demonstrates implementation structure, evaluation discipline, and domain translation. It does not claim production deployment, real compliance validation, robot hardware deployment, or customer adoption.

## Highest-Signal Projects

| Project | Evidence to inspect | What is real | What is mocked or synthetic |
| --- | --- | --- | --- |
| [AEC Code Compliance RAG](projects/aec-code-compliance-rag/README.md) | Primary review project: RAG, citations, eval, and AEC domain fit. | Markdown/PDF ingestion, source manifests, metadata filters, page-aware chunking, Singapore public-source downloader for BCA/URA/NEA/SCDF/LTA/PUB/NParks, TF-IDF/BM25/dense LSA/hybrid retrieval, optional embedding/reranking modes, ablation report, citation formatting, eval script, demo outputs, tests. | Synthetic guidance by default; public PDFs downloaded locally and not committed; no scanned PDF OCR, authority approval, or legal/code advice. |
| [Agentic Research Ops Assistant](projects/agentic-research-ops-assistant/README.md) | Agent orchestration, tool registry, approval gate, traces. | Planner/executor flow, local search, tool traces, SQLite persistence, trace eval. | Local demo docs; deterministic tools; not autonomous web research. |
| [MLOps Model Serving Monitoring](projects/mlops-model-serving-monitoring/README.md) | Model lifecycle, serving schema, logging, drift report. | Training pipeline, artifact metadata, FastAPI-compatible functions, SQLite logs, PSI-style drift checks. | Synthetic churn data; local registry; no production alerting. |
| [Fine-Tuning LoRA Lab](projects/fine-tuning-lora-lab/README.md) | Honest adaptation workflow and dataset discipline. | Dataset generation, validation, split checks, LoRA config, eval template. | Training is mocked; no model weights are updated. |
| [Multimodal VLM Visual QA](projects/multimodal-vlm-visual-qa/README.md) | Multimodal product boundary and structured outputs. | Image validation, prompt contract, schema parsing, mock provider, optional OpenAI-compatible path. | Mock mode does not perform real visual reasoning. |
| [VLA Embodied Agent Simulator](projects/vla-embodied-agent-simulator/README.md) | Construction-site embodied AI simulation with safety constraints. | Language-to-action parser, grid environment, action masks, policy baselines, safety-shielded planning, metrics, replay traces, and tests. | No robot hardware, ROS, SLAM, perception model, learned policy, or real-world safety validation. |

## Review Path

The strongest code paths are concentrated in the primary AEC project, its evaluation docs, and one supporting system depending on role: agent workflows, MLOps, fine-tuning workflow, or VLM product boundary.

Key evidence files:

- Primary project: [projects/aec-code-compliance-rag](projects/aec-code-compliance-rag/README.md)
- AEC evaluation: [AEC EVAL.md](projects/aec-code-compliance-rag/EVAL.md)
- AEC architecture: [AEC ARCHITECTURE.md](projects/aec-code-compliance-rag/ARCHITECTURE.md)
- Focused tests: [tests/test_rag.py](tests/test_rag.py)
- Full local verification: `python scripts/verify.py`

## Focused Verification

```bash
python scripts/generate_sample_data.py
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py
python projects/aec-code-compliance-rag/scripts/download_public_sources.py
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py --corpus public
python -m pytest tests/test_rag.py
streamlit run projects/aec-code-compliance-rag/app.py
```

Evidence produced by those commands:

- AEC citations and no-answer behavior.
- `demo_outputs/` artifacts for generated evidence.
- Local test and evaluation output for the primary RAG workflow.

## 60-Minute Technical Verification

```bash
python scripts/verify.py
python -m pytest
python -m ruff check .
python -m black --check .
python scripts/check_repo_health.py
python scripts/check_portfolio_site.py
python scripts/run_smoke_tests.py
python scripts/check_project_docs.py
```

Code areas with the clearest signal:

- RAG: `projects/aec-code-compliance-rag/src/aec_code_compliance_rag/`
- Agent traces: `projects/agentic-research-ops-assistant/src/agentic_research_ops_assistant/`
- MLOps observability: `projects/mlops-model-serving-monitoring/src/mlops_model_serving_monitoring/`
- Fine-tuning workflow: `projects/fine-tuning-lora-lab/src/fine_tuning_lora_lab/workflow.py`
- VLM provider boundary: `projects/multimodal-vlm-visual-qa/src/multimodal_vlm_visual_qa/`
- VLA simulation: `projects/vla-embodied-agent-simulator/src/vla_embodied_agent_simulator/`

## What Is Implemented Versus Prototype

| Category | Meaning in this repo |
| --- | --- |
| Real implementation | Local code paths that run and are tested: retrieval, schema validation, mock providers, artifact writing, trace/log persistence, drift calculations. |
| Mock provider | Deterministic substitute for an LLM/VLM so the workflow can be tested without paid APIs. |
| Synthetic data | Generated/demo data with no customer, employer, or private project content. |
| Prototype | A runnable local skeleton that shows engineering shape but lacks production data, monitoring, security, and scale. |
| Local engineering scaffold | A small local version of a real concern, such as SQLite inference logs, model metadata, citation objects, trace records, eval cases, or drift reports. |

## Skills Demonstrated

- RAG: Markdown/PDF ingestion, Singapore public-source downloads, source manifests, metadata-filtered retrieval, page-aware chunking, retrieval scoring, citations, evaluation, no-answer handling.
- LLM applications: provider abstraction, structured outputs, prompt contracts, uncertainty fields.
- Agents: planning, tool calls, approval gates, traces, persistence, trace evaluation.
- MLOps: training pipeline, model artifact metadata, inference logging, drift detection, monitoring report.
- Multimodal AI: image validation, VLM provider boundary, schema parsing, mock/hosted distinction.
- Fine-tuning workflow: dataset validation, LoRA config planning, eval templates, hardware honesty.
- Built-environment AI: AEC document-assistance workflow, BIM QA, construction robotics/safety simulations.
- Embodied AI: language-to-action parsing, action masks, simulated safety constraints, baseline policy comparison, and replayable traces.

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
python scripts/check_portfolio_site.py
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
- Do not infer real-world code-compliance capability from synthetic examples or downloaded public-source retrieval demos.
- Do not infer real visual reasoning from mock VLM outputs.
- Do not infer real LoRA model improvement from the fine-tuning lab.
- Do not infer senior-level MLOps ownership from the local MLOps skeleton.

## Supporting Docs

- [How to review this portfolio](docs/how-to-review-this-portfolio.md)
- [Technical review guide](docs/technical-review-guide.md)
- [Reviewer guide](docs/REVIEWER_GUIDE.md)
- [Claims policy](docs/CLAIMS_POLICY.md)
- [Authenticity and ownership](docs/AUTHENTICITY_AND_OWNERSHIP.md)
- [Demo recording guide](docs/DEMO_RECORDING_GUIDE.md)

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
