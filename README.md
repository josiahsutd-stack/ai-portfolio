# Josiah Lau | Applied AI Engineering Portfolio

Applied AI engineer focused on source-grounded AI, embodied-agent simulation, and measurable local ML systems, with domain experience in architecture and the built environment.

This repository is designed for technical review: the main projects run without paid APIs, checked-in outputs are labeled by data source, and claims are bounded by tests, evaluations, and explicit limitations.

## Recruiter Fast Path

Start with these three projects. They carry the clearest evidence and represent different parts of the candidate's applied AI profile.

| Priority | Project | Evidence | Current local result | Boundary |
| --- | --- | --- | --- | --- |
| 1 - Flagship | [AEC Code Compliance RAG](projects/aec-code-compliance-rag/README.md) | Public-source ingestion, page-aware chunks, four retrieval modes, citations, abstention, 51-case synthetic regression set, and focused tests. | Hybrid retrieval: `Recall@4 1.000`, `MRR 0.906`, `Hit@3 1.000` on the bundled synthetic eval. | Document-assistance prototype; not compliance certification or professional advice. |
| 2 - Embodied AI | [VLA Embodied Agent Simulator](projects/vla-embodied-agent-simulator/README.md) | Language-to-task parsing, action masks, construction-site constraints, three policy baselines, metrics, and replay traces. | Safety-shielded policy: `3/3` simulated scenarios completed with `0.000` unsafe-action rate. | Deterministic 2D grid simulation; no learned VLA model, perception stack, ROS, or hardware validation. |
| 3 - Model Training | [Real Model Fine-Tune Lab](projects/real-model-finetune-lab/README.md) | Real TF-IDF/logistic-regression fitting, fixed splits, dummy baseline, held-out metrics, confusion matrix, and generated weights. | Compact UCI SMS subset: `0.975` accuracy and macro-F1 on a 40-row test split. | Small classical-ML exercise; not transformer fine-tuning or a benchmark claim. |

The metric values above are regression evidence for the included datasets and scenarios. They are not claims of real-world compliance, robot safety, or production model quality.

![Portfolio site showing the evidence-first project hierarchy](docs/assets/screenshots/portfolio-home.png)

## Run Evidence Locally

Python 3.11 or newer is recommended.

```bash
python -m pip install -r requirements.txt -r requirements-dev.txt
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py
python projects/vla-embodied-agent-simulator/evaluate_vla.py
python projects/real-model-finetune-lab/evaluate_model.py
python -m pytest tests/test_rag.py tests/test_vla_embodied_agent.py tests/test_real_model_finetune_lab.py
```

Full repository verification:

```bash
python scripts/verify.py
```

`scripts/verify.py` regenerates synthetic fixtures and review artifacts, checks repository health, public claims, Markdown links, and the static site, imports every project, enforces artifact idempotence, runs formatting and lint checks, and executes the full pytest suite. Versioned review outputs exclude machine-dependent timestamps and timings so a successful run leaves the tracked tree unchanged.

## Flagship Evidence

### AEC Code Compliance RAG

The flagship converts bundled synthetic guidance or locally downloaded Singapore public documents into metadata-rich chunks, retrieves evidence with TF-IDF, BM25, dense LSA, or hybrid search, and returns citation-bearing answers or an explicit abstention.

- [Architecture](projects/aec-code-compliance-rag/ARCHITECTURE.md)
- [Evaluation design and results](projects/aec-code-compliance-rag/EVAL.md)
- [Generated review outputs](projects/aec-code-compliance-rag/demo_outputs/)
- [Public-source inventory and provenance notes](projects/aec-code-compliance-rag/public_sources/SOURCE_NOTES.md)
- [Focused tests](tests/test_rag.py)
- [Design write-up](docs/AEC_RAG_DESIGN_WRITEUP.md)

Optional Singapore public-source workflow:

```bash
python projects/aec-code-compliance-rag/scripts/download_public_sources.py
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py --corpus public
```

The downloader targets official BCA, URA, NEA, SCDF, LTA, PUB, and NParks sources. Downloaded files remain local and are not redistributed. Public retrieval demonstrates provenance-aware ingestion; it does not validate document currency or confer authority approval.

![AEC RAG local Streamlit demo with source citations](docs/assets/screenshots/aec-rag-demo.png)

## Supporting Systems

| Project | What is implemented | Honest interpretation |
| --- | --- | --- |
| [Agentic Research Ops Assistant](projects/agentic-research-ops-assistant/README.md) | Deterministic planner, permissioned tool registry, local retrieval, citations, retries, approval gates, SQLite traces, and trace evaluation. | Evidence of inspectable agent workflow engineering, not autonomous research or live web access. |
| [MLOps Model Serving Monitoring](projects/mlops-model-serving-monitoring/README.md) | Synthetic churn training, FastAPI schema, generated artifact metadata, SQLite prediction logs, drift calculations, and monitoring reports. | Local operations scaffold, not a deployed platform or real customer system. |

These systems are substantial supporting projects, but the repository does not present them as production deployments.

## Experiments And Baselines

The remaining projects are deliberately tiered below the flagship and supporting systems. They demonstrate narrower workflows, baselines, or interface contracts rather than comparable depth.

<details>
<summary>View experiments and baselines</summary>

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

</details>

## Evidence Labels

| Label | Meaning in this repository |
| --- | --- |
| Real local implementation | Runnable and tested code for retrieval, validation, model fitting, persistence, metrics, or simulation. |
| Public-source subset | Public data or documents with source notes; still limited in size and review scope. |
| Synthetic data | Generated demo data containing no customer, employer, private-project, or confidential content. |
| Mock provider | Deterministic LLM/VLM substitute used to test workflow contracts without paid services. |
| Simulation | Locally evaluated environment behavior; no physical robot or real-world safety claim. |
| Generated artifact | Reproducible output from an evaluation command. Runtime model binaries and databases are ignored by Git. |

## Repository Map

```text
projects/                 project code, project-level evidence, and limitations
tests/                    cross-project and focused regression tests
scripts/                  setup, verification, claim, site, and artifact checks
docs/                     reviewer guides, design notes, and portfolio-wide boundaries
portfolio-site/           static evidence-first portfolio view
shared/                   small reusable local AI utilities
```

## Reviewer Guides

- [Five- and fifteen-minute review paths](docs/how-to-review-this-portfolio.md)
- [Technical review guide](docs/technical-review-guide.md)
- [Role-specific reviewer guide](docs/REVIEWER_GUIDE.md)
- [Scope and limitations](docs/SCOPE_AND_LIMITATIONS.md)
- [Claims policy](docs/CLAIMS_POLICY.md)
- [Authenticity and ownership](docs/AUTHENTICITY_AND_OWNERSHIP.md)

## Static Portfolio

```bash
python -m http.server 8080 --directory portfolio-site
```

Then open `http://localhost:8080`.

## Contact

- [GitHub](https://github.com/josiahsutd-stack)
- [LinkedIn](https://www.linkedin.com/in/josiah-lau-8041822b6/)
- Email is available in application materials.
