# Project Evidence Inventory

This inventory is the interpretation guide for all 19 project directories. Folder and package slugs remain stable for existing commands; public names describe the current implementation rather than an aspirational capability.

## Evidence Tiers

| Tier | Meaning |
| --- | --- |
| Flagship | Deepest source, evaluation, failure-analysis, and documentation surface. |
| Primary | Strong focused evidence for a distinct skill area, with measured limitations. |
| Supporting | Substantial workflow engineering that strengthens the primary review path. |
| Experiment | Narrow baseline or interface contract; useful context, not equal evidence of depth. |

## Complete Inventory

| Tier | Project | Implemented evidence | Hard boundary |
| --- | --- | --- | --- |
| Flagship | [AEC Code Compliance RAG Assistant](aec-code-compliance-rag/README.md) | Four local retrieval modes, page-aware metadata, citations, abstention, 51-case regression evaluation, and optional official-public-source ingestion. | Not compliance certification, legal advice, or proof that public documents are current. |
| Primary | [Construction Embodied Agent Simulator](vla-embodied-agent-simulator/README.md) | Random-forest behavior cloning, disjoint procedural holdout scenarios, closed-loop evaluation, A* reference, action filtering, and failure traces. | Structured grid state only; no foundation VLA, perception, physics, ROS, or hardware. |
| Primary | [Local Text Classification Lab](real-model-finetune-lab/README.md) | TF-IDF plus logistic-regression fitting, dummy baselines, deterministic source-traceable splits, held-out metrics, confusion matrix, and generated model binaries. | Classical supervised learning, not pretrained-model fine-tuning or a benchmark result. |
| Supporting | [Deterministic Research Workflow Assistant](agentic-research-ops-assistant/README.md) | Rule-based planning, permissioned tools, local retrieval, retries, citations, approval gates, SQLite traces, and trace evaluation. | Not an adaptive LLM planner, autonomous researcher, or live web agent. |
| Supporting | [Local Model Serving and Monitoring Scaffold](mlops-model-serving-monitoring/README.md) | Random-forest training, FastAPI schemas, joblib metadata, SQLite prediction logs, PSI drift checks, and monitoring reports. | Not a deployed registry, orchestration system, alerting service, or production monitor. |
| Experiment | [Construction Progress Metadata Classifier](construction-progress-cv/README.md) | Random-forest classification over synthetic site-image metadata. | No image pixels or computer-vision model. |
| Experiment | [BIM Schedule Rule Checker](bim-issue-detection-agent/README.md) | Deterministic schedule rules, severity scoring, and optional explanation formatting. | No geometric BIM parsing, clash detection, or professional QA. |
| Experiment | [AI/AEC Job Description Match Baseline](ai-aec-job-fit-analyzer/README.md) | Transparent keyword matching between job text and a supplied skill profile. | Not a learned hiring model or evidence of candidate suitability. |
| Experiment | [Building Energy Regression Pipeline](building-energy-ml-pipeline/README.md) | Random-forest regression over synthetic building-performance rows. | Not calibrated simulation or professional energy analysis. |
| Experiment | [Spatial Design Scoring Baseline](spatial-design-recommender/README.md) | Explicit weighted rules over synthetic layout attributes. | Not generative design, optimization, or validated architectural advice. |
| Experiment | [Construction Grid Route Planner](construction-robot-task-planner/README.md) | Deterministic A* routing through synthetic site constraints. | No perception, motion physics, ROS, or robot actuation. |
| Experiment | [Robot Telemetry Safety Rule Monitor](site-robot-safety-monitor/README.md) | Explicit proximity, speed, payload, and emergency-stop rules over synthetic telemetry. | Not a certified safety system or physical robot validation. |
| Experiment | [Visual QA Provider Contract](multimodal-vlm-visual-qa/README.md) | Image-byte validation, request construction, structured response parsing, zero-confidence mock, and optional hosted-provider path. | No local VLM, OCR, visual reasoning, or defect-detection evidence. |
| Experiment | [Sequential Decision Simulation Baselines](reinforcement-learning-portfolio/README.md) | Inventory and pricing environments with random and hand-written policy evaluation. | No learned policy, Q-learning, DQN, PPO, or policy gradients. |
| Experiment | [Vision Baseline / Threshold Model Lab](deep-learning-vision-lab/README.md) | Programmatic 16x16 images and deterministic bright-pixel classification. | No neural network, learned visual representation, or real-image benchmark. |
| Experiment | [Prompt and Output Validation Checks](llm-evals-guardrails-platform/README.md) | Prompt-pattern, JSON-schema, citation-coverage, and regression-case checks. | Not a comprehensive safety, security, or guardrail platform. |
| Experiment | [Content-Based Ranking Baseline](recommender-system-ranking-engine/README.md) | Popularity and TF-IDF content-similarity ranking with small offline metrics. | No collaborative model, online feedback, or production ranking evaluation. |
| Experiment | [Time-Series Forecast and Anomaly Baselines](time-series-anomaly-forecasting/README.md) | Moving-average forecast and deterministic anomaly threshold over synthetic traffic. | No learned forecasting model, uncertainty intervals, or operational alerting. |
| Experiment | [LoRA Dataset and Configuration Validator](fine-tuning-lora-lab/README.md) | Instruction-row validation, duplicate and split checks, LoRA configuration, and simulated run report. | No pretrained model, tokenizer, adapter training, GPU run, or updated parameters. |

The authoritative machine-readable version of the same hierarchy is [`projects.yml`](projects.yml). Repository verification rejects missing boundaries, unsupported tiers, title drift, duplicate slugs, more than five projects above experiment tier, or capability-heavy project names that the current implementation does not support.
