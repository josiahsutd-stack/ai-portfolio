# Repository Audit

Audit date: 2026-06-18

## Current Project Structure

The repository contains 18 projects under `projects/`:

- 8 built-environment projects covering AEC RAG, construction CV, BIM QA, energy ML, spatial recommendations, and construction robotics.
- 10 general AI engineering projects covering VLMs, agents, VLA simulation, RL, deep vision, LLMOps, MLOps, recommenders, time-series ML, and LoRA workflow.

Shared code lives under `shared/`, setup scripts under `scripts/`, docs under `docs/`, and tests under `tests/`.

## Projects Found

Flagship projects:

- Agentic Research Operations Assistant
- Multimodal VLM Visual QA Assistant
- VLA Embodied Agent Simulator
- MLOps Model Serving and Monitoring Platform
- LLM Evals and Guardrails Platform

Secondary projects:

- Reinforcement Learning Portfolio
- Deep Learning Vision Lab
- Recommender System Ranking Engine
- Time-Series Anomaly Detection and Forecasting
- AEC Code Compliance RAG Assistant
- BIM Issue Detection Agent
- Building Energy ML Pipeline
- Construction robotics projects

## Issues Found

- Project READMEs had runnable demo commands but did not consistently include `Engineering Notes` or recruiter-facing technical review discussion sections.
- Documentation was split across older built-environment docs and newer general-AI docs, creating naming overlap.
- CI workflow existed as `tests.yml`; the preferred structure is `ci.yml`.
- There was no repo-level health check or smoke test script.
- The repo needed a recruiter/hiring-manager review guide and troubleshooting guide.
- The repo had project metadata only in human-readable tables, not a machine-readable file.
- Several projects are intentionally lightweight and are labeled as local-demo or experimental where appropriate.

## Broken Or Incomplete Areas

- GitHub Actions may fail to start because of the account-level GitHub Actions billing lock already observed. This is not a code failure.
- Some optional integrations are placeholders: real VLM providers, LoRA training on GPU, ROS/robotics stacks, and hosted LLM providers.
- Some demos use transparent baselines instead of heavy models to keep local setup fast.

## Duplicate Code

- Streamlit app bootstrapping repeats across projects. This is acceptable for demo clarity, but future cleanup could add a small shared app-path helper.
- Mock provider patterns exist in multiple projects. The shared `shared/ai/providers.py` covers LLMs, while project-specific VLM mock behavior remains local to the VLM project.

## Inconsistent Naming

- Older docs used names like `ai-skills-matrix.md`; new preferred docs add `skills-matrix.md` and keep older docs as compatibility references.
- The workflow file is being standardized to `ci.yml`.

## Missing READMEs / Tests / Imports

- No project README files were missing.
- Tests existed for core behavior; additional smoke and health checks were added.
- Import smoke checks are now covered by `scripts/run_smoke_tests.py`.

## Missing Dependencies

- Current runnable demos use the existing lightweight dependencies: FastAPI, Streamlit, pandas, NumPy, scikit-learn, Pydantic, pytest, Ruff, and Black.
- PyTorch, Gymnasium, transformers, and FAISS/Chroma are documented as optional future extensions and are not required for local quick mode.

## Commands Checked

- `python -m pytest`
- `python -m ruff check .`
- `python scripts/check_project_docs.py`
- Browser audit of portfolio pages in local Chrome

## Recommended Fixes Implemented

- Added repo health and smoke scripts.
- Added project metadata at `projects/projects.yml`.
- Added audit, troubleshooting, technical review guide, role map, skills matrix, and roadmap docs.
- Added shared package placeholders for evals, schemas, and testing.
- Added Makefile commands for setup, test, smoke, health, demo, format, lint, and clean.
- Updated `.env.example` for mock/local mode.
- Standardized project README expectations through health checks.

## Remaining Recommendations

- Add screenshot or short GIF evidence for the 5 flagship projects.
- Deepen flagship project internals over time rather than making all projects equally complex.
- Add SQLite persistence to LLM evals and MLOps logging.
- Add optional real provider implementations behind the existing mock/provider abstractions.
