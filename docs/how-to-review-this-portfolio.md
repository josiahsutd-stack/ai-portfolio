# How To Review This Portfolio

## 5-Minute Review Path

1. Read the top of `README.md`.
2. Open `projects/aec-code-compliance-rag/README.md`.
3. Review `projects/aec-code-compliance-rag/EVAL.md`.
4. Skim one supporting review project: Agentic Research Ops or MLOps Model Serving Monitoring.
5. Skim `docs/technical-review-guide.md`.

## 15-Minute Review Path

1. Run `python scripts/verify.py`.
2. Run the primary demo: `streamlit run projects/aec-code-compliance-rag/app.py`.
3. Run the primary eval: `python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py`.
4. Optional deeper AEC check: `python projects/aec-code-compliance-rag/scripts/download_public_sources.py` then `python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py --corpus public`.
5. Review `projects/projects.yml`.
6. Inspect `tests/test_rag.py`.

## Top 3 For A General AI Recruiter

1. `projects/aec-code-compliance-rag` - best evidence of domain RAG, citations, Singapore public-source ingestion, evals, limitations, and runnable local artifacts.
2. `projects/agentic-research-ops-assistant` - best evidence of agent workflow design, tool traces, citations, approval checkpoints, and trace persistence.
3. `projects/mlops-model-serving-monitoring` - best evidence of model-serving hygiene, metadata, schema validation, prediction logging, and drift reports.

The fine-tuning and VLM projects are useful supporting evidence, but they should not be inspected before the top 3 unless the role is specifically adaptation or multimodal.

## Best Projects By Role

| Role | Best projects to inspect |
| --- | --- |
| AI Engineer | AEC Code Compliance RAG, Agentic Research Ops, MLOps Platform |
| ML Engineer | MLOps Platform, Building Energy ML, Time-Series Forecasting |
| LLM / Agent Engineer | AEC Code Compliance RAG, Agentic Research Ops, LLM Evals Guardrails |
| Computer Vision / VLM | Multimodal VLM Visual QA, Vision Baseline Lab, Construction Progress CV |
| MLOps | MLOps Platform, LLM Evals Guardrails, Vision Baseline Lab |
| Robotics / VLA | VLA Simulator as experimental simulation, Construction Robot Task Planner, Site Robot Safety Monitor |
| Fine-tuning workflow | Fine-Tuning LoRA Lab, LLM Evals Guardrails, AEC RAG |

## How To Run Demos

```bash
python scripts/generate_sample_data.py
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py
python projects/aec-code-compliance-rag/scripts/download_public_sources.py
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py --corpus public
python projects/vla-embodied-agent-simulator/evaluate_vla.py
streamlit run projects/aec-code-compliance-rag/app.py
```

All demos run without API keys in mock/local mode. The VLM project can optionally use an OpenAI-compatible hosted vision provider when `VLM_PROVIDER=openai` and `OPENAI_API_KEY` are set.

## What Is Synthetic Or Mock

- Sample data is synthetic by default; the AEC project can optionally download public Singapore BCA/URA/NEA/SCDF/LTA/PUB/NParks sources for local retrieval tests.
- LLM/VLM providers fall back to mock mode.
- Robotics and VLA projects are simulations.
- LoRA training is mocked locally to avoid GPU requirements.
