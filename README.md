# AI for the Built Environment Portfolio

Applied AI engineering portfolio for a candidate with a master's background in AI, architecture, and embodied AI, plus experience in building, architecture, and construction workflows.

The repository is designed to be honest, runnable, and recruiter-friendly. It uses synthetic/demo data, local-first AI abstractions, and practical end-to-end workflows instead of tutorial notebooks.

## Positioning

AI Engineer focused on applied AI, embodied AI, LLM systems, computer vision, and automation for real-world built-environment workflows.

## Featured Projects

| Project | What it proves | Demo |
| --- | --- | --- |
| [AEC Code Compliance RAG Assistant](projects/aec-code-compliance-rag/README.md) | LLM engineering, RAG, retrieval, citations, AEC document workflows | `streamlit run projects/aec-code-compliance-rag/app.py` |
| [Construction Progress CV Tracker](projects/construction-progress-cv/README.md) | Computer vision workflow design, ML classification, reporting automation | `streamlit run projects/construction-progress-cv/app.py` |
| [BIM Issue Detection Agent](projects/bim-issue-detection-agent/README.md) | Structured data validation, agentic explanations, design QA automation | `streamlit run projects/bim-issue-detection-agent/app.py` |
| [AI + AEC Job Fit Analyzer](projects/ai-aec-job-fit-analyzer/README.md) | NLP classification, structured outputs, product thinking | `streamlit run projects/ai-aec-job-fit-analyzer/app.py` |
| [Building Energy ML Pipeline](projects/building-energy-ml-pipeline/README.md) | Classic ML, feature engineering, evaluation, API deployment | `streamlit run projects/building-energy-ml-pipeline/app.py` |
| [Spatial Design Recommender](projects/spatial-design-recommender/README.md) | Recommendation systems, explainable scoring, design automation | `streamlit run projects/spatial-design-recommender/app.py` |
| [Construction Robot Task Planner](projects/construction-robot-task-planner/README.md) | Embodied AI planning, robot navigation constraints, construction robotics | `streamlit run projects/construction-robot-task-planner/app.py` |
| [Site Robot Safety Monitor](projects/site-robot-safety-monitor/README.md) | Human-robot safety, telemetry analysis, embodied AI monitoring | `streamlit run projects/site-robot-safety-monitor/app.py` |

## Local Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
python scripts/generate_sample_data.py
pytest
```

On macOS/Linux, activate the environment with `source .venv/bin/activate`.

## Run The Portfolio Site

Open [portfolio-site/index.html](portfolio-site/index.html) in a browser, or serve it locally:

```bash
python -m http.server 8080 --directory portfolio-site
```

## Run APIs

```bash
python -m uvicorn construction_progress_cv.api:app --app-dir projects/construction-progress-cv/src --reload
python -m uvicorn bim_issue_detection_agent.api:app --app-dir projects/bim-issue-detection-agent/src --reload
python -m uvicorn building_energy_ml_pipeline.api:app --app-dir projects/building-energy-ml-pipeline/src --reload
python -m uvicorn spatial_design_recommender.api:app --app-dir projects/spatial-design-recommender/src --reload
python -m uvicorn construction_robot_task_planner.api:app --app-dir projects/construction-robot-task-planner/src --reload
python -m uvicorn site_robot_safety_monitor.api:app --app-dir projects/site-robot-safety-monitor/src --reload
```

## Docker Example

Build project images from the repository root:

```bash
docker build -f projects/building-energy-ml-pipeline/Dockerfile -t built-env-energy-demo .
docker run --rm -p 8501:8501 built-env-energy-demo
```

Use the same `docker build -f projects/<project>/Dockerfile -t <name> .` pattern for the Streamlit project demos.

## Data And Honesty Notes

- All included data is synthetic/demo data.
- The projects do not claim employer, client, or production outcomes.
- LLM features use a local mock provider when no `OPENAI_API_KEY` is configured.
- AEC outputs are not legal, code, engineering, or professional compliance advice.

## Repository Structure

```text
.
├── profile-readme.md
├── portfolio-site/
├── projects/
│   ├── aec-code-compliance-rag/
│   ├── construction-progress-cv/
│   ├── bim-issue-detection-agent/
│   ├── ai-aec-job-fit-analyzer/
│   ├── building-energy-ml-pipeline/
│   ├── spatial-design-recommender/
│   ├── construction-robot-task-planner/
│   └── site-robot-safety-monitor/
├── shared/
│   ├── ai/
│   ├── data/
│   └── utils/
├── docs/
├── scripts/
└── tests/
```

## Customize Before Publishing

- Replace placeholder name, location, email, LinkedIn, and GitHub links.
- Add screenshots to each project README after running demos.
- Add a real resume link only if it is ready and public-safe.
- Keep project claims as portfolio work unless real production evidence exists.
