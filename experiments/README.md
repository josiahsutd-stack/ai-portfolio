# Experiments And Baselines

These studies isolate one baseline, rule system, or provider contract at a time. They remain runnable and tested because they record useful implementation decisions, but they are intentionally outside the selected project set and do not support the portfolio's headline claims.

| Experiment | Implemented evidence | Hard boundary |
| --- | --- | --- |
| [BIM Schedule Rule Checker](bim-schedule-rule-checker/README.md) | Deterministic schedule rules, severity scoring, and optional explanation formatting. | No geometric BIM parsing, clash detection, or professional QA. |
| [Building Energy Regression Experiment](building-energy-ml-pipeline/README.md) | Random-forest regression with a fixed synthetic holdout and mean baseline. | Not calibrated simulation or professional energy analysis. |
| [Construction Grid Route Planner](construction-robot-task-planner/README.md) | Deterministic A* routing through synthetic site constraints. | No perception, motion physics, ROS, or robot actuation. |
| [Robot Telemetry Safety Rule Monitor](site-robot-safety-monitor/README.md) | Explicit proximity, speed, payload, and emergency-stop rules over synthetic telemetry. | Not a certified safety system or physical robot validation. |
| [Visual Provider Contract](visual-provider-contract/README.md) | Image-byte validation, request construction, structured parsing, zero-confidence mock, and optional hosted-provider path. | No local VLM, OCR, visual reasoning, or defect-detection evidence. |
| [Deterministic Research Workflow Assistant](agentic-research-ops-assistant/README.md) | Rule-based planning, permissioned tools, local retrieval, retries, approval gates, SQLite traces, and trace evaluation. | Not an adaptive LLM planner, autonomous researcher, or live web agent. |
| [Local Model Serving and Monitoring Scaffold](mlops-model-serving-monitoring/README.md) | Synthetic model training, FastAPI schemas, joblib metadata, SQLite prediction logs, PSI drift checks, and reports. | Not a deployed registry, orchestration system, alerting service, or production monitor. |
| [Local Text Classification Lab](local-text-classification-lab/README.md) | TF-IDF plus logistic-regression fitting, source-traceable splits, dummy baseline, held-out metrics, confusion matrix, and generated weights. | Classical supervised learning on compact datasets, not pretrained-model fine-tuning or a benchmark claim. |

The retained set favors domain-relevant rule systems and locally evaluated engineering contracts over generic breadth. All commands run from the repository root. `python scripts/verify.py` exercises both selected projects and experiments.
