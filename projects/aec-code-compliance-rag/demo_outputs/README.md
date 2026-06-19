# Demo Outputs

This folder stores reviewer-facing outputs generated from synthetic demo data.

Regenerate the artifacts from the repository root:

```bash
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py
```

Expected generated files:

- `retrieval_eval_summary.json`
- `retrieval_eval_report.md`
- `retrieval_ablation_summary.json`
- `retrieval_ablation_report.md`
- `accessible_route_answer.md`
- `no_answer_failure_case.md`
