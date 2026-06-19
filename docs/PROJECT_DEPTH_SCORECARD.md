# Project Depth Scorecard

| Project | Depth level | Tested | Eval artifacts | Real model/API | Mock/synthetic boundary | Best reviewer file | Improvement priority |
| --- | --- | --- | --- | --- | --- | --- | --- |
| AEC Code Compliance RAG | flagship | yes | yes | local lexical retrieval | synthetic AEC docs; no compliance advice | `projects/aec-code-compliance-rag/EVAL.md` | expand corpus and citation faithfulness |
| Agentic Research Ops Assistant | flagship | yes | yes | deterministic local planner | local docs only; not web research | `projects/agentic-research-ops-assistant/demo_outputs/agent_eval_report.md` | richer tool failure evals |
| MLOps Model Serving Monitoring | flagship | yes | yes | scikit-learn local model | synthetic churn data; not production monitoring | `projects/mlops-model-serving-monitoring/demo_outputs/model_eval_report.md` | delayed-label simulation |
| Multimodal VLM Visual QA | supporting | yes | partial | optional hosted provider | mock mode is not visual reasoning | `projects/multimodal-vlm-visual-qa/LIMITATIONS.md` | add local visual baseline or keep demoted |
| Fine-Tuning LoRA Lab | supporting | yes | partial | no real training | mock training; no weights updated | `projects/fine-tuning-lora-lab/EVAL.md` | real PEFT run when hardware allows |
| Construction Robot Task Planner | supporting | yes | no | deterministic planner | synthetic site grid | `projects/construction-robot-task-planner/README.md` | richer constraints |
| Site Robot Safety Monitor | supporting | yes | no | rules over synthetic telemetry | no hardware deployment | `projects/site-robot-safety-monitor/README.md` | scenario evals |
| Remaining projects | experiment | mixed | limited | local baselines | synthetic/demo data | project README files | keep secondary unless deepened |
