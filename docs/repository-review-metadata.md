# Repository Review Metadata

This file summarizes public repository metadata that helps recruiters and hiring teams understand the portfolio quickly.

## Repository Description

Applied and embodied AI engineering portfolio for built-environment workflows: RAG, BIM QA, CV-style progress tracking, construction robotics, energy ML, VLM workflows, agents, MLOps, LLM evals, and spatial recommendations.

## Suggested Topics

```text
ai-engineering embodied-ai robotics rag fastapi streamlit machine-learning computer-vision aec bim construction-tech proptech built-environment llm-agents mlops
```

## Local Verification

The repository is designed to be tested without private datasets or paid API keys:

```bash
pip install -r requirements.txt -r requirements-dev.txt
python scripts/generate_sample_data.py
python scripts/check_repo_health.py
python scripts/run_smoke_tests.py
pytest
```

## Public Review Notes

- Contact links are intentionally kept in the root README and profile README rather than repeated in every project.
- Screenshots should represent actual local demo runs using synthetic data.
- Mock provider behavior is documented where real APIs or heavy local models are not required for repository review.
