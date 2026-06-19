# Applied AI Engineering Portfolio

Applied AI engineer focused on source-grounded LLM systems, agent workflows, MLOps workflows, multimodal product interfaces, and built-environment AI.

This repository is intentionally local-first: projects run with synthetic data or mock providers so reviewers can inspect engineering structure without private datasets, paid APIs, or hidden services.

Live demo placeholder: [AEC RAG live demo](https://example.com/aec-rag-demo-placeholder) - replace this URL after deployment.

## Portfolio Highlights

This portfolio focuses on applied AI engineering work that is runnable locally and documented with tests, evaluation scripts, architecture notes, and sample outputs.

![Portfolio site screenshot](docs/assets/screenshots/portfolio-home.png)

| Project | What it demonstrates | Evidence |
| --- | --- | --- |
| [AEC Code Compliance RAG](projects/aec-code-compliance-rag/README.md) | Source-grounded retrieval, Singapore public-source ingestion, citation formatting, no-answer handling, and AEC domain translation. | [EVAL.md](projects/aec-code-compliance-rag/EVAL.md), [public source notes](projects/aec-code-compliance-rag/public_sources/SOURCE_NOTES.md), [demo outputs](projects/aec-code-compliance-rag/demo_outputs/), [tests](tests/test_rag.py) |
| [Agentic Research Ops Assistant](projects/agentic-research-ops-assistant/README.md) | Planner-executor workflow, tool traces, approval checkpoints, citations, and local persistence. | [ARCHITECTURE.md](projects/agentic-research-ops-assistant/ARCHITECTURE.md), [demo outputs](projects/agentic-research-ops-assistant/demo_outputs/), trace evaluation |
| [MLOps Model Serving Monitoring](projects/mlops-model-serving-monitoring/README.md) | Model metadata, schema validation, prediction logging, drift reporting, and monitoring docs. | [MODEL_CARD.md](projects/mlops-model-serving-monitoring/MODEL_CARD.md), [MONITORING.md](projects/mlops-model-serving-monitoring/MONITORING.md), [demo outputs](projects/mlops-model-serving-monitoring/demo_outputs/) |
| [Real Model Fine-Tune Lab](projects/real-model-finetune-lab/README.md) | Actual model fitting on a small text-classification dataset with before/after metrics and saved weights. | demo outputs, saved model artifact, tests |

The projects use synthetic data and mock providers where needed, so the repository can be reviewed without private datasets, paid APIs, or hidden services.

## Quick Verification

```bash
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py
python projects/aec-code-compliance-rag/scripts/download_public_sources.py
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py --corpus public
python -m pytest tests/test_rag.py tests/test_general_ai_projects.py
python projects/real-model-finetune-lab/evaluate_model.py
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

This is a local-first engineering portfolio. It demonstrates implementation structure, evaluation discipline, and domain translation. See [Scope and limitations](docs/SCOPE_AND_LIMITATIONS.md) for full caveats.

## Project Tiers

### Tier 1 - Flagship (Deep)

| Project | Why it is tiered here |
| --- | --- |
| [AEC Code Compliance RAG](projects/aec-code-compliance-rag/README.md) | Source-grounded AEC RAG with Markdown/PDF ingestion, page-aware chunks, Singapore public-source downloader for BCA/URA/NEA/SCDF/LTA/PUB/NParks, retrieval ablations, citations, no-answer handling, demo outputs, architecture docs, and tests. |

### Tier 2 - Supporting Systems

| Project | Why it is tiered here |
| --- | --- |
| [Agentic Research Ops Assistant](projects/agentic-research-ops-assistant/README.md) | Planner/executor workflow with local tools, citations, approval checkpoints, SQLite persistence, trace outputs, and trace evaluation. |
| [MLOps Model Serving Monitoring](projects/mlops-model-serving-monitoring/README.md) | Model metadata, schema validation, prediction logging, drift checks, monitoring docs, and generated model artifacts. |
| [Real Model Fine-Tune Lab](projects/real-model-finetune-lab/README.md) | Actual fitted text classifier with before/after metrics, saved model weights, demo outputs, and regression tests. |
| [VLA Embodied Agent Simulator](projects/vla-embodied-agent-simulator/README.md) | Construction-site language-to-action simulator with action masks, safety-shielded planning, baseline comparisons, metrics, and replay traces. |

### Tier 3 - Experiments / Baselines

These broaden the portfolio and remain useful, but they are smaller scaffolds or baselines rather than deep systems:

- [Construction Progress CV Workflow Tracker](projects/construction-progress-cv/README.md)
- [BIM Issue Detection Agent](projects/bim-issue-detection-agent/README.md)
- [AI + AEC Job Fit Analyzer](projects/ai-aec-job-fit-analyzer/README.md)
- [Building Energy ML Pipeline](projects/building-energy-ml-pipeline/README.md)
- [Spatial Design Recommendation Engine](projects/spatial-design-recommender/README.md)
- [Construction Robot Task Planner](projects/construction-robot-task-planner/README.md)
- [Site Robot Safety Monitor](projects/site-robot-safety-monitor/README.md)
- [Multimodal VLM Visual QA](projects/multimodal-vlm-visual-qa/README.md)
- [Reinforcement Learning Portfolio](projects/reinforcement-learning-portfolio/README.md)
- [Vision Baseline / Threshold Model Lab](projects/deep-learning-vision-lab/README.md)
- [LLM Evals and Guardrails Platform](projects/llm-evals-guardrails-platform/README.md)
- [Recommender System Ranking Engine](projects/recommender-system-ranking-engine/README.md)
- [Time-Series Anomaly Detection and Forecasting](projects/time-series-anomaly-forecasting/README.md)
- [Fine-Tuning LoRA Lab](projects/fine-tuning-lora-lab/README.md)

## What's Real Vs. Mocked

| Category | Meaning in this repo |
| --- | --- |
| Real local implementation | Runnable code paths, tests, eval scripts, saved artifacts, trace logs, retrieval metrics, model metadata, or fitted classical ML weights. |
| Mock provider | Deterministic substitute for an LLM/VLM so workflow logic can be tested without paid APIs. |
| Synthetic data | Generated demo data with no customer, employer, private project, or confidential content. |
| Simulation | Robotics/VLA/RL behavior is evaluated in local simulated environments, not hardware. |
| Full limitations | The longer caveat list lives in [docs/SCOPE_AND_LIMITATIONS.md](docs/SCOPE_AND_LIMITATIONS.md). |

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
- Real fitted model: `projects/real-model-finetune-lab/src/real_model_finetune_lab/`
- VLM provider boundary: `projects/multimodal-vlm-visual-qa/src/multimodal_vlm_visual_qa/`
- VLA simulation: `projects/vla-embodied-agent-simulator/src/vla_embodied_agent_simulator/`

## Skills Demonstrated

- RAG: Markdown/PDF ingestion, Singapore public-source downloads, source manifests, metadata-filtered retrieval, page-aware chunking, retrieval scoring, citations, evaluation, no-answer handling.
- LLM applications: provider abstraction, structured outputs, prompt contracts, uncertainty fields.
- Agents: planning, tool calls, approval gates, traces, persistence, trace evaluation.
- MLOps: training pipeline, model artifact metadata, inference logging, drift detection, monitoring report.
- Multimodal AI: image validation, VLM provider boundary, schema parsing, mock/hosted distinction.
- Fine-tuning workflow: dataset validation, LoRA config planning, eval templates, hardware honesty, plus one real fitted classifier project.
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

## Supporting Docs

- [How to review this portfolio](docs/how-to-review-this-portfolio.md)
- [Technical review guide](docs/technical-review-guide.md)
- [Reviewer guide](docs/REVIEWER_GUIDE.md)
- [Claims policy](docs/CLAIMS_POLICY.md)
- [Scope and limitations](docs/SCOPE_AND_LIMITATIONS.md)
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
- LinkedIn placeholder: `https://www.linkedin.com/in/<your-linkedin-handle>`
- Email: listed in application materials
- Contact email placeholder: `<your.email@example.com>`
