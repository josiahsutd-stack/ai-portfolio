# Headline Evidence Ledger

This recruiter-facing ledger maps each headline result to the versioned JSON artifact and local command that produced it. The values are regenerated and checked for drift by `scripts/check_evidence_claims.py`.

| Project | Evaluation scope | Current artifact-backed result | Versioned evidence | Reproduce | Interpretation boundary |
| --- | --- | --- | --- | --- | --- |
| [AEC Code Compliance RAG Assistant](../projects/aec-code-compliance-rag/README.md) | Bundled synthetic retrieval and abstention regression set | Recall@4 1.000; MRR 0.906; Hit@3 1.000; 51 cases | [`retrieval_eval_summary.json`](../projects/aec-code-compliance-rag/demo_outputs/retrieval_eval_summary.json) | `python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py` | Document-assistance prototype, not compliance certification or professional advice |
| [Construction Embodied Agent Simulator](../projects/vla-embodied-agent-simulator/README.md) | Fixed-seed disjoint procedural construction-grid holdout | Filtered policy success 0.625; unsafe-action rate 0.000; raw success 0.500; 24 holdout scenarios | [`behavior_cloning_eval_summary.json`](../projects/vla-embodied-agent-simulator/demo_outputs/behavior_cloning_eval_summary.json) | `python projects/vla-embodied-agent-simulator/evaluate_vla.py` | No foundation VLA, perception, physics, ROS, hardware, or physical-safety validation |
| [Local Text Classification Lab](../projects/real-model-finetune-lab/README.md) | Deterministic source-traceable 160/40/40 split of a compact balanced UCI SMS subset | Test accuracy 0.950; macro-F1 0.950; baseline accuracy 0.500; 40 test rows | [`public_sms_metrics.json`](../projects/real-model-finetune-lab/demo_outputs/public_sms_metrics.json) | `python projects/real-model-finetune-lab/evaluate_model.py` | Classical supervised learning, not pretrained-model fine-tuning or a benchmark claim |

## Integrity Gate

The evidence configuration is stored in [`evidence_claims.yml`](evidence_claims.yml). Each metric names an exact JSON path and display precision. The checker fails when an artifact is missing, a JSON path changes, a displayed value becomes stale, or this generated ledger differs from the current artifacts.

The full local and CI gate is:

```bash
python scripts/verify.py
```

These measurements describe only the bundled datasets and simulator scenarios. They are not production, customer, compliance, or physical-safety results.
