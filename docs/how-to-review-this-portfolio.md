# How To Review This Portfolio

## 5-Minute Review Path

1. Read the top of `README.md`.
2. Open `projects/aec-code-compliance-rag/README.md`.
3. Review `projects/aec-code-compliance-rag/EVAL.md`.
4. Skim one supporting flagship: agent, MLOps, fine-tuning, or VLM.
5. Skim `docs/technical-review-guide.md`.

## 15-Minute Review Path

1. Run `python scripts/verify.py`.
2. Run the flagship demo: `streamlit run projects/aec-code-compliance-rag/app.py`.
3. Run the flagship eval: `python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py`.
4. Review `projects/projects.yml`.
5. Inspect `tests/test_rag.py`.

## Best Projects By Role

| Role | Best projects to inspect |
| --- | --- |
| AI Engineer | AEC Code Compliance RAG, Agentic Research Ops, MLOps Platform |
| ML Engineer | MLOps Platform, Building Energy ML, Time-Series Forecasting |
| LLM / Agent Engineer | AEC Code Compliance RAG, Agentic Research Ops, LLM Evals Guardrails |
| Computer Vision / VLM | Multimodal VLM Visual QA, Deep Vision Lab, Construction Progress CV |
| MLOps | MLOps Platform, LLM Evals Guardrails, Deep Vision Lab |
| Robotics / VLA | Construction Robot Task Planner, Site Robot Safety Monitor, VLA Simulator as experimental simulation |
| Fine-tuning workflow | Fine-Tuning LoRA Lab, LLM Evals Guardrails, AEC RAG |

## How To Run Demos

```bash
python scripts/generate_sample_data.py
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py
streamlit run projects/aec-code-compliance-rag/app.py
```

All demos run without API keys in mock/local mode. The VLM project can optionally use an OpenAI-compatible hosted vision provider when `VLM_PROVIDER=openai` and `OPENAI_API_KEY` are set.

## What Is Synthetic Or Mock

- Sample data is synthetic.
- LLM/VLM providers fall back to mock mode.
- Robotics and VLA projects are simulations.
- LoRA training is mocked locally to avoid GPU requirements.
