# Reproducible Evidence Ledger

This ledger maps selected quantitative results to versioned JSON artifacts and the local commands that produced them. Values and metric-bearing scope text are regenerated and checked for drift by `scripts/check_evidence_claims.py`.

| Project | Evaluation scope | Current artifact-backed result | Versioned evidence | Reproduce | Interpretation boundary |
| --- | --- | --- | --- | --- | --- |
| [AEC Code Compliance RAG Assistant](../projects/aec-code-compliance-rag/README.md) | Bundled synthetic retrieval and abstention regression set | Recall@4 1.000; MRR 0.906; Hit@3 1.000; 51 cases | [`retrieval_eval_summary.json`](../projects/aec-code-compliance-rag/demo_outputs/retrieval_eval_summary.json) | `python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py` | Document-assistance prototype, not compliance certification or professional advice |
| [Construction Embodied Agent Simulator](../projects/vla-embodied-agent-simulator/README.md) | Fixed-seed disjoint procedural construction-grid holdout | Filtered policy success 0.625; unsafe-action rate 0.000; raw success 0.500; 24 holdout scenarios | [`behavior_cloning_eval_summary.json`](../projects/vla-embodied-agent-simulator/demo_outputs/behavior_cloning_eval_summary.json) | `python projects/vla-embodied-agent-simulator/evaluate_vla.py` | No foundation VLA, perception, physics, ROS, hardware, or physical-safety validation |
| [Local Text Classification Lab](../projects/real-model-finetune-lab/README.md) | Deterministic source-traceable 160/40/40 split of a compact balanced UCI SMS subset | Test accuracy 0.950; macro-F1 0.950; baseline accuracy 0.500; 40 test rows | [`public_sms_metrics.json`](../projects/real-model-finetune-lab/demo_outputs/public_sms_metrics.json) | `python projects/real-model-finetune-lab/evaluate_model.py` | Classical supervised learning, not pretrained-model fine-tuning or a benchmark claim |
| [Building Energy Regression Experiment](../experiments/building-energy-ml-pipeline/README.md) | Fixed 135/45 split of 180 bundled synthetic building rows | Random-forest MAE 30.29 and R2 0.579 vs mean-baseline MAE 42.50; 45 synthetic holdout rows | [`energy_eval_summary.json`](../experiments/building-energy-ml-pipeline/demo_outputs/energy_eval_summary.json) | `python experiments/building-energy-ml-pipeline/evaluate_model.py` | Not calibrated energy simulation or professional performance analysis |
| [Robot Telemetry Safety Rule Monitor](../experiments/site-robot-safety-monitor/README.md) | Deterministic rule execution over 36 bundled unlabeled synthetic telemetry rows | 26 rule events (19 high, 7 medium) from 36 synthetic rows; no labeled accuracy evaluation | [`safety_monitor_demo_summary.json`](../experiments/site-robot-safety-monitor/demo_outputs/safety_monitor_demo_summary.json) | `python experiments/site-robot-safety-monitor/generate_demo_report.py` | Not a certified safety system or physical robot validation |

## Integrity Gate

The evidence configuration is stored in [`evidence_claims.yml`](evidence_claims.yml). Each metric names an exact JSON path and display precision. The checker fails when an artifact is missing, a JSON path changes, a displayed value becomes stale, or this generated ledger differs from the current artifacts.

The full local and CI gate is:

```bash
python scripts/verify.py
```

These measurements describe only the bundled datasets and simulator scenarios. They are not production, customer, compliance, or physical-safety results.
