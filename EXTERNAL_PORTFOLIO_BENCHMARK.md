# External Portfolio Benchmark

This benchmark uses public repositories and engineering references for conceptual comparison only. No wording, diagrams, project names, code, or visual identity were copied.

## Repositories / References Reviewed

| Source | What makes it strong | Conceptual lesson for this repo | What not to copy |
| --- | --- | --- | --- |
| [GokuMohandas/Made-With-ML](https://github.com/GokuMohandas/Made-With-ML) | End-to-end ML system framing with lessons, code, deployment, iteration, and software-engineering discipline. | Favor fewer deep systems with clear lifecycle evidence over many shallow demos. | Do not copy lesson structure or wording. |
| [Full Stack Deep Learning text recognizer labs](https://github.com/the-full-stack/fsdl-text-recognizer-2022-labs) | Incrementally builds a full DL application with setup, modeling, deployment, and CI-oriented thinking. | Show architecture and reproducible commands for flagship projects. | Do not imitate the educational lab format. |
| [DataTalksClub MLOps Zoomcamp](https://github.com/DataTalksClub/mlops-zoomcamp) | Covers training, deployment, monitoring, and project work in a structured MLOps path. | MLOps projects should include monitoring, logging, reproducibility, and operational vocabulary. | Do not imply course completion or copy homework/project formats. |
| [ZenML Projects](https://github.com/zenml-io/zenml-projects) | Demonstrates reusable MLOps workflows and domain examples with clear pipeline framing. | Add local monitoring reports and model metadata even without full orchestration. | Do not claim enterprise readiness. |
| [Microsoft GraphRAG](https://github.com/microsoft/graphrag) | Strong documentation around indexing, graph construction, and query flow. | Only mention graph approaches as future work unless graph construction/eval is implemented. | Do not add GraphRAG branding without graph logic. |
| [Hugging Face PEFT](https://github.com/huggingface/peft) | Clear separation between parameter-efficient methods, supported tasks, and training requirements. | Fine-tuning lab should be explicit about hardware and what training is mocked. | Do not imply PEFT integration unless real training code exists. |
| [LLaVA](https://github.com/haotian-liu/llava) | Shows that serious VLM projects release training/eval scripts and benchmark context. | VLM demo must clearly separate mock workflow validation from real visual reasoning. | Do not claim LLaVA-style capability. |
| [MLflow Model Registry docs](https://mlflow.org/docs/latest/ml/model-registry/) | Model versions, aliases, tags, and metadata are first-class lifecycle objects. | Local MLOps skeleton should store version, schema, metrics, dataset info, and commit metadata. | Do not add MLflow dependency unless it is actually used. |

## Comparison Against This Repo

This repo is strongest where it is domain-specific and honest: AEC RAG, built-environment workflows, and local runnable demos. It is weaker than strong public examples in depth per project, screenshots/demo evidence, and mature operational scaffolding.

## Improvements Adapted Conceptually

- Focus the first review path on 3-5 projects.
- Add architecture and evaluation docs to the strongest projects.
- Add demo outputs so reviewers can inspect behavior without running everything.
- Add monitoring/report artifacts for MLOps.
- Keep mock/synthetic labels prominent.
- Treat limitations as credibility, not apology.

## Improvements Not Adapted

- No heavy orchestration framework was added.
- No GraphRAG claim was added.
- No real fine-tuning claim was added.
- No production deployment claim was added.
- No copied README structure, diagrams, or project concepts were used.
