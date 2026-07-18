# Selected Project Evidence

Only the five projects with the strongest implementation and evaluation evidence live in this directory. The machine-readable hierarchy remains in [`projects.yml`](projects.yml).

| Tier | Project | Implemented evidence | Hard boundary |
| --- | --- | --- | --- |
| Flagship | [AEC Code Compliance RAG Assistant](aec-code-compliance-rag/README.md) | Four local retrieval modes, page-aware metadata, citations, abstention, 51-case regression evaluation, and optional official-public-source ingestion. | Not compliance certification, legal advice, or proof that public documents are current. |
| Primary | [Construction Embodied Agent Simulator](vla-embodied-agent-simulator/README.md) | Random-forest behavior cloning, disjoint procedural holdout scenarios, closed-loop evaluation, A* reference, action filtering, and failure traces. | Structured grid state only; no foundation VLA, perception, physics, ROS, or hardware. |
| Primary | [Local Text Classification Lab](real-model-finetune-lab/README.md) | TF-IDF plus logistic-regression fitting, dummy baselines, source-traceable splits, held-out metrics, confusion matrix, and generated model binaries. | Classical supervised learning, not pretrained-model fine-tuning or a benchmark result. |
| Supporting | [Deterministic Research Workflow Assistant](agentic-research-ops-assistant/README.md) | Rule-based planning, permissioned tools, local retrieval, retries, citations, approval gates, SQLite traces, and trace evaluation. | Not an adaptive LLM planner, autonomous researcher, or live web agent. |
| Supporting | [Local Model Serving and Monitoring Scaffold](mlops-model-serving-monitoring/README.md) | Random-forest training, FastAPI schemas, joblib metadata, SQLite prediction logs, PSI drift checks, and monitoring reports. | Not a deployed registry, orchestration system, alerting service, or production monitor. |

The [experiment inventory](../experiments/README.md) records narrower baselines separately. Repository verification checks both locations, but only these five projects appear in the selected-work path.
