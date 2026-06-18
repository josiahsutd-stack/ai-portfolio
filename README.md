# Applied and General AI Engineering Portfolio

AI engineer focused on applied AI systems, LLM agents, multimodal AI, machine learning, and automation - with a unique background in architecture and the built environment.

This portfolio combines domain-specific AI for the built environment with general AI engineering projects across VLMs, agents, reinforcement learning, deep learning, MLOps, recommender systems, time-series ML, and fine-tuning workflows.

## Recommended Review Path For Recruiters

If you are reviewing my portfolio, I recommend starting with these five projects because they show the strongest mix of AI engineering range, product thinking, and my built-environment/embodied AI specialization:

- [Agentic Research Operations Assistant](projects/agentic-research-ops-assistant/README.md) - planner/executor agent, tool calling, local RAG, citations, and approval checkpoints.
- [Multimodal VLM Visual QA Assistant](projects/multimodal-vlm-visual-qa/README.md) - VLM product workflow, provider abstraction, structured visual QA output, and mock/provider boundary.
- [VLA Embodied Agent Simulator](projects/vla-embodied-agent-simulator/README.md) - embodied AI loop from language and state to safe actions.
- [MLOps Model Serving and Monitoring Platform](projects/mlops-model-serving-monitoring/README.md) - training, serving, drift checks, model metadata, Docker, and tests.
- [AEC Code Compliance RAG Assistant](projects/aec-code-compliance-rag/README.md) - built-environment differentiator with RAG, citations, and compliance-oriented uncertainty handling.

## Why I Structured This Portfolio This Way

I designed this repository for two kinds of hiring review:

- If you are hiring for general AI engineering, I recommend reviewing the agents, VLM, LLM evals, MLOps, RL, recommender, time-series, and fine-tuning projects.
- If you are hiring for built-environment, robotics, or embodied AI work, I recommend reviewing the AEC document, BIM QA, construction progress, energy modeling, spatial design, and construction robotics projects.
- I kept every project runnable locally with synthetic data or mock providers so you can inspect the engineering without needing private datasets, paid APIs, or hidden infrastructure.

## Project Table

| Project | Skill area | What it proves | Tech stack | Demo command | Resume bullet |
| --- | --- | --- | --- | --- | --- |
| [AEC Code Compliance RAG](projects/aec-code-compliance-rag/README.md) | RAG / AEC | Source-grounded LLM workflows | Python, Streamlit, TF-IDF | `streamlit run projects/aec-code-compliance-rag/app.py` | Built a RAG assistant for AEC guidance with chunking, retrieval, citations, and mock LLM fallback. |
| [Construction Progress CV](projects/construction-progress-cv/README.md) | CV / ML | Progress classification and reporting | Python, scikit-learn, FastAPI | `streamlit run projects/construction-progress-cv/app.py` | Built a construction progress tracker that classifies synthetic site metadata and generates reports. |
| [BIM Issue Detection Agent](projects/bim-issue-detection-agent/README.md) | Agents / Data QA | Structured design QA automation | Python, pandas, Streamlit | `streamlit run projects/bim-issue-detection-agent/app.py` | Built a BIM QA agent that flags room schedule issues and exports explainable reports. |
| [AI + AEC Job Fit Analyzer](projects/ai-aec-job-fit-analyzer/README.md) | NLP / Product | Role classification and gap analysis | Python, Streamlit | `streamlit run projects/ai-aec-job-fit-analyzer/app.py` | Built a job-fit analyzer that classifies AI/AEC roles and returns application strategy. |
| [Building Energy ML](projects/building-energy-ml-pipeline/README.md) | Classic ML | Feature engineering, evaluation, API | Python, scikit-learn, FastAPI | `streamlit run projects/building-energy-ml-pipeline/app.py` | Built an energy prediction pipeline with synthetic data, evaluation, API, and model card. |
| [Spatial Design Recommender](projects/spatial-design-recommender/README.md) | Recommendations | Explainable spatial design scoring | Python, FastAPI, Streamlit | `streamlit run projects/spatial-design-recommender/app.py` | Built a spatial recommender that scores layout scenarios and suggests design improvements. |
| [Construction Robot Task Planner](projects/construction-robot-task-planner/README.md) | Embodied AI | Safety-aware robot planning | Python, Streamlit, FastAPI | `streamlit run projects/construction-robot-task-planner/app.py` | Built a construction robot planner with obstacle, payload, and battery constraints. |
| [Site Robot Safety Monitor](projects/site-robot-safety-monitor/README.md) | Robotics safety | Telemetry risk detection | Python, pandas, FastAPI | `streamlit run projects/site-robot-safety-monitor/app.py` | Built a robot safety monitor that flags proximity, obstacle, payload, and emergency-stop events. |
| [Multimodal VLM Visual QA](projects/multimodal-vlm-visual-qa/README.md) | VLM / Multimodal | Image QA, schemas, uncertainty | Python, Streamlit, FastAPI | `streamlit run projects/multimodal-vlm-visual-qa/app.py` | Built a multimodal visual QA assistant with VLM provider abstraction and structured JSON extraction. |
| [Agentic Research Ops](projects/agentic-research-ops-assistant/README.md) | Agentic AI / RAG | Planning, tools, citations, HITL | Python, Streamlit, Pydantic | `streamlit run projects/agentic-research-ops-assistant/app.py` | Built a planner-executor research agent with local RAG, tool calls, citations, and approval checkpoints. |
| [VLA Embodied Simulator](projects/vla-embodied-agent-simulator/README.md) | VLA / Robotics | Language-state-action planning | Python, Streamlit | `streamlit run projects/vla-embodied-agent-simulator/app.py` | Created a VLA-inspired simulator that maps instructions and grid state into safe actions. |
| [Reinforcement Learning Portfolio](projects/reinforcement-learning-portfolio/README.md) | RL | Environments, rewards, policy eval | Python, Streamlit | `streamlit run projects/reinforcement-learning-portfolio/app.py` | Implemented RL simulations for inventory control and dynamic pricing with baseline policies. |
| [Deep Learning Vision Lab](projects/deep-learning-vision-lab/README.md) | DL / CV | Dataset, metrics, inference API | Python, NumPy, FastAPI | `streamlit run projects/deep-learning-vision-lab/app.py` | Built a synthetic defect detection lab with metrics, model card, demo, and API endpoint. |
| [LLM Evals Guardrails](projects/llm-evals-guardrails-platform/README.md) | LLMOps | Prompt injection and schema checks | Python, Streamlit, FastAPI | `streamlit run projects/llm-evals-guardrails-platform/app.py` | Built an LLM evals platform for prompt injection, structured output, and citation checks. |
| [MLOps Serving Monitoring](projects/mlops-model-serving-monitoring/README.md) | MLOps | Serving, schema, drift detection | Python, scikit-learn, FastAPI | `streamlit run projects/mlops-model-serving-monitoring/app.py` | Built an MLOps demo with training, FastAPI serving, drift detection, Docker, and tests. |
| [Recommender Ranking Engine](projects/recommender-system-ranking-engine/README.md) | Recommendations | Ranking, metrics, explanations | Python, scikit-learn, FastAPI | `streamlit run projects/recommender-system-ranking-engine/app.py` | Built a recommender with popularity/content baselines, precision@k, and NDCG@k. |
| [Time-Series Anomaly Forecasting](projects/time-series-anomaly-forecasting/README.md) | Time-series ML | Forecasting, anomaly alerts | Python, scikit-learn, FastAPI | `streamlit run projects/time-series-anomaly-forecasting/app.py` | Built a time-series forecasting and anomaly-detection system with backtesting metrics. |
| [Fine-Tuning LoRA Lab](projects/fine-tuning-lora-lab/README.md) | Fine-tuning | Dataset prep and LoRA workflow | Python, Streamlit | `streamlit run projects/fine-tuning-lora-lab/app.py` | Built a compute-aware LoRA workflow with dataset validation, mock trainer, and model card. |

## AI For The Built Environment

These projects preserve the differentiator: AI plus architecture, AEC, construction, BIM, energy, spatial design, and construction robotics.

- AEC Code Compliance RAG Assistant
- Construction Progress Computer Vision Tracker
- BIM / Drawing Issue Detection Agent
- AI + AEC Job Fit Analyzer
- Building Energy Prediction ML Pipeline
- Spatial Design Recommendation Engine
- Construction Robot Task Planner
- Site Robot Safety Monitor

## General AI Engineering Projects

- Multimodal VLM Visual QA Assistant
- Agentic Research Operations Assistant
- VLA Embodied Agent Simulator
- Reinforcement Learning Portfolio
- Deep Learning Vision Lab
- LLM Evals and Guardrails Platform
- MLOps Model Serving and Monitoring Platform
- Recommender System Ranking Engine
- Time-Series Anomaly Detection and Forecasting
- Fine-Tuning and LoRA Lab

## Skills Coverage Matrix

See [docs/skills-matrix.md](docs/skills-matrix.md), [docs/role-to-project-map.md](docs/role-to-project-map.md), and [portfolio-site/pages/skills-matrix.html](portfolio-site/pages/skills-matrix.html).

## Quickstart

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
python scripts/generate_sample_data.py
python scripts/check_repo_health.py
python scripts/run_smoke_tests.py
pytest
```

On macOS/Linux, activate with `source .venv/bin/activate`.

## Run Tests And Quality Checks

```bash
python -m black --check .
python -m ruff check .
python scripts/check_repo_health.py
python scripts/run_smoke_tests.py
python -m pytest
python scripts/check_project_docs.py
```

The Makefile provides the same common checks where `make` is available:

```bash
make health
make smoke
make test
```

## Reviewer Guides

- [How to review this portfolio](docs/how-to-review-this-portfolio.md)
- [Technical review guide](docs/technical-review-guide.md)
- [Repository review metadata](docs/repository-review-metadata.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Repo audit](docs/repo-audit.md)
- [Project roadmap](docs/project-roadmap.md)

## Portfolio Site

Open [portfolio-site/index.html](portfolio-site/index.html), or run:

```bash
python -m http.server 8080 --directory portfolio-site
```

## Docker Example

Build project images from the repository root:

```bash
docker build -f projects/mlops-model-serving-monitoring/Dockerfile -t ai-portfolio-mlops .
docker run --rm -p 8000:8000 ai-portfolio-mlops
```

Use the same `docker build -f projects/<project>/Dockerfile -t <name> .` pattern for projects with Dockerfiles.

## Repository Structure

```text
.
|-- profile-readme.md
|-- portfolio-site/
|-- projects/
|   |-- aec-code-compliance-rag/
|   |-- construction-progress-cv/
|   |-- bim-issue-detection-agent/
|   |-- building-energy-ml-pipeline/
|   |-- construction-robot-task-planner/
|   |-- multimodal-vlm-visual-qa/
|   |-- agentic-research-ops-assistant/
|   |-- vla-embodied-agent-simulator/
|   |-- reinforcement-learning-portfolio/
|   |-- deep-learning-vision-lab/
|   |-- llm-evals-guardrails-platform/
|   |-- mlops-model-serving-monitoring/
|   |-- recommender-system-ranking-engine/
|   |-- time-series-anomaly-forecasting/
|   `-- fine-tuning-lora-lab/
|-- shared/
|-- docs/
|-- scripts/
`-- tests/
```

## Roadmap

See [docs/project-roadmap.md](docs/project-roadmap.md) and [docs/project-priority-roadmap.md](docs/project-priority-roadmap.md).

## Synthetic And Mock Notes

- All data is synthetic/demo data unless explicitly stated otherwise.
- LLM/VLM projects run in mock mode without paid APIs.
- VLA and robotics projects are simulations, not real robot deployments.
- Fine-tuning uses a mock training path locally and documents where real GPU training would fit.
- AEC outputs are not legal, code, engineering, or professional compliance advice.
- No production users, clients, employers, or performance claims are fabricated.

## Contact

- GitHub: `https://github.com/josiahsutd-stack`
- LinkedIn: listed in application materials
- Email: listed in application materials
