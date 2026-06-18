# How To Review This Portfolio

## 5-Minute Review Path

1. Read the top of `README.md`.
2. Inspect the flagship project table.
3. Open `projects/agentic-research-ops-assistant/README.md`.
4. Open `projects/mlops-model-serving-monitoring/README.md`.
5. Skim `docs/role-to-project-map.md`.

## 15-Minute Review Path

1. Run `python scripts/run_smoke_tests.py`.
2. Run one demo: `streamlit run projects/agentic-research-ops-assistant/app.py`.
3. Inspect `tests/test_general_ai_projects.py`.
4. Review `projects/projects.yml`.
5. Read the Engineering Notes section in two project READMEs.

## Best Projects By Role

| Role | Best projects to inspect |
| --- | --- |
| AI Engineer | Agentic Research Ops, MLOps Platform, VLM Visual QA |
| ML Engineer | MLOps Platform, Building Energy ML, Time-Series Forecasting |
| LLM / Agent Engineer | Agentic Research Ops, LLM Evals Guardrails, AEC RAG |
| Computer Vision / VLM | Multimodal VLM Visual QA, Deep Vision Lab, Construction Progress CV |
| MLOps | MLOps Platform, LLM Evals Guardrails, Deep Vision Lab |
| RL / VLA | VLA Simulator, RL Portfolio, Construction Robot Task Planner |

## How To Run Demos

```bash
python scripts/generate_sample_data.py
streamlit run projects/agentic-research-ops-assistant/app.py
```

All demos run without API keys in mock/local mode.

## What Is Synthetic Or Mock

- Sample data is synthetic.
- LLM/VLM providers fall back to mock mode.
- Robotics and VLA projects are simulations.
- LoRA training is mocked locally to avoid GPU requirements.

