# How To Review This Portfolio

## 5-Minute Review Path

1. Read the top of `README.md`.
2. Inspect the flagship project section.
3. Open `projects/aec-code-compliance-rag/README.md`.
4. Open `projects/mlops-model-serving-monitoring/README.md`.
5. Skim `docs/technical-review-guide.md`.

## 15-Minute Review Path

1. Run `python scripts/verify.py`.
2. Run one demo: `streamlit run projects/mlops-model-serving-monitoring/app.py`.
3. Inspect `tests/test_general_ai_projects.py`.
4. Review `projects/projects.yml`.
5. Read the Engineering Notes section in two project READMEs.

## Best Projects By Role

| Role | Best projects to inspect |
| --- | --- |
| AI Engineer | Agentic Research Ops, MLOps Platform, LLM Evals Guardrails |
| ML Engineer | MLOps Platform, Building Energy ML, Time-Series Forecasting |
| LLM / Agent Engineer | Agentic Research Ops, LLM Evals Guardrails, AEC RAG |
| Computer Vision / VLM | Multimodal VLM Visual QA, Deep Vision Lab, Construction Progress CV |
| MLOps | MLOps Platform, LLM Evals Guardrails, Deep Vision Lab |
| Robotics / VLA | Construction Robot Task Planner, Site Robot Safety Monitor, VLA Simulator as experimental simulation |

## How To Run Demos

```bash
python scripts/generate_sample_data.py
streamlit run projects/mlops-model-serving-monitoring/app.py
```

All demos run without API keys in mock/local mode. The VLM project can optionally use an OpenAI-compatible hosted vision provider when `VLM_PROVIDER=openai` and `OPENAI_API_KEY` are set.

## What Is Synthetic Or Mock

- Sample data is synthetic.
- LLM/VLM providers fall back to mock mode.
- Robotics and VLA projects are simulations.
- LoRA training is mocked locally to avoid GPU requirements.
