# Experiments And Baselines

These studies isolate one baseline, rule system, or provider contract at a time. They remain runnable and tested because they document useful implementation decisions, but they are intentionally excluded from the selected project tree and do not support the portfolio's headline claims.

| Experiment | Implemented evidence | Hard boundary |
| --- | --- | --- |
| [QS Takeoff and Tender Analysis Workbench](qs-takeoff-tender-analysis/README.md) | Shared-wall vector measurement, opening deductions, rate provenance, uncertainty bands, and tender exception checks over hand-calculated synthetic fixtures. | No PDF/CAD/BIM parsing, live pricing, professional QS output, or award recommendation. |
| [BIM Schedule Rule Checker](bim-issue-detection-agent/README.md) | Deterministic schedule rules, severity scoring, and optional explanation formatting. | No geometric BIM parsing, clash detection, or professional QA. |
| [Project Brief and Specification Copilot](project-specification-copilot/README.md) | Role-tagged messages, requirement lifecycle, conflict detection, approval gates, SQLite audit events, and source-linked draft clauses over synthetic conversations. | Deterministic phrase set; no authenticated authority, open-domain understanding, or professional specification. |
| [Building Energy Regression Experiment](building-energy-ml-pipeline/README.md) | Random-forest regression with a fixed synthetic holdout and mean baseline. | Not calibrated simulation or professional energy analysis. |
| [Constraint-Aware Massing Explorer](constraint-aware-massing-explorer/README.md) | Seeded geometric options, hard constraints, Pareto ranking, baseline evaluation, and generated SVG comparisons over three synthetic sites. | Rectangular proxy model; no code inference, internal egress, calibrated environmental simulation, or approvable design. |
| [Construction Grid Route Planner](construction-robot-task-planner/README.md) | Deterministic A* routing through synthetic site constraints. | No perception, motion physics, ROS, or robot actuation. |
| [Robot Telemetry Safety Rule Monitor](site-robot-safety-monitor/README.md) | Explicit proximity, speed, payload, and emergency-stop rules over synthetic telemetry. | Not a certified safety system or physical robot validation. |
| [Visual QA Provider Contract](multimodal-vlm-visual-qa/README.md) | Image-byte validation, request construction, structured parsing, zero-confidence mock, and optional hosted-provider path. | No local VLM, OCR, visual reasoning, or defect-detection evidence. |
| [Sequential Decision Simulation Baselines](reinforcement-learning-portfolio/README.md) | Inventory and pricing environments with random and hand-written policy evaluation. | No learned policy, Q-learning, DQN, PPO, or policy gradients. |
| [Vision Threshold Baseline Lab](deep-learning-vision-lab/README.md) | Programmatic 16x16 images and deterministic bright-pixel classification. | No neural network, learned visual representation, or real-image benchmark. |
| [Prompt And Output Validation Checks](llm-evals-guardrails-platform/README.md) | Prompt-pattern, JSON-schema, citation-coverage, and regression-case checks. | Not a comprehensive safety, security, or guardrail platform. |
| [Content-Based Ranking Baseline](recommender-system-ranking-engine/README.md) | Popularity and TF-IDF content-similarity ranking with small offline metrics. | No collaborative model, online feedback, or production ranking evaluation. |
| [Time-Series Forecast And Anomaly Baselines](time-series-anomaly-forecasting/README.md) | Moving-average forecast and deterministic anomaly threshold over synthetic traffic. | No learned forecasting model, uncertainty intervals, or operational alerting. |
| [LoRA Dataset And Configuration Validator](fine-tuning-lora-lab/README.md) | Instruction-row validation, duplicate and split checks, LoRA configuration, and simulated run report. | No pretrained model, tokenizer, adapter training, GPU run, or updated parameters. |

All commands in the experiment READMEs run from the repository root. `python scripts/verify.py` exercises both selected projects and experiments.
