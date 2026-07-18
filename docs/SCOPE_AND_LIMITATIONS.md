# Scope And Limitations

This portfolio is a local-first applied AI engineering portfolio. It demonstrates implementation structure, evaluation discipline, and domain translation through runnable code, tests, generated artifacts, and project documentation.

## What Is Implemented Versus Prototype

| Category | Meaning in this repo |
| --- | --- |
| Real implementation | Local code paths that run and are tested: retrieval, schema validation, fitted scikit-learn models, mock providers, artifact writing, trace/log persistence, drift calculations, citation objects, eval cases, and replay traces. |
| Mock provider | Deterministic substitute for an LLM/VLM so workflow behavior can be tested without paid APIs. |
| Synthetic data | Generated/demo data with no customer, employer, private project, or confidential content. |
| Prototype | A runnable local skeleton that shows engineering shape but lacks production data, monitoring, security, scale, and user adoption. |
| Local engineering scaffold | A small local version of a real concern, such as SQLite inference logs, model metadata, citation objects, trace records, eval cases, or drift reports. |

## Honest Limitations

- No real users, customers, deployments, adoption, benchmark wins, or paid-client outcomes are claimed.
- All included datasets are synthetic unless a file explicitly says otherwise.
- Mock LLM/VLM paths validate workflow behavior, not model intelligence.
- AEC outputs are not legal, code, engineering, architectural, or professional compliance advice.
- The original Fine-Tuning LoRA Lab does not update real model weights locally; the separate Real Model Fine-Tune Lab trains a small classical ML model.
- Robotics projects are simulations, not robot hardware deployments.
- CI may be blocked by GitHub account state even when local tests pass.

## What Not To Infer

- Do not infer production reliability from local demos.
- Do not infer real-world code-compliance capability from synthetic examples or downloaded public-source retrieval demos.
- Do not infer real visual reasoning from mock VLM outputs.
- Do not infer real LoRA model improvement from the Fine-Tuning LoRA Lab.
- Do not infer senior-level MLOps ownership from the local MLOps skeleton.
- Do not infer real robot safety validation from construction-robot, embodied-agent, or reinforcement-learning simulations.

## Where The Strongest Evidence Lives

- AEC RAG depth: `projects/aec-code-compliance-rag/`
- Agent workflow depth: `projects/agentic-research-ops-assistant/`
- MLOps workflow depth: `projects/mlops-model-serving-monitoring/`
- Real model fitting: `projects/real-model-finetune-lab/`
- Embodied AI simulation: `projects/vla-embodied-agent-simulator/`
