# Demo Outputs

This folder stores versioned outputs generated from the synthetic demo corpus. The optional Singapore public-source evaluation writes the same artifact shape under `public_sources/`.

Regenerate the artifacts from the repository root:

```bash
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py
```

Optional Singapore public-source artifacts:

```bash
python projects/aec-code-compliance-rag/scripts/download_public_sources.py
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py --corpus public
```

Expected generated files:

- `retrieval_eval_summary.json`
- `retrieval_eval_report.md`
- `retrieval_ablation_summary.json`
- `retrieval_ablation_report.md`
- `accessible_route_answer.md`
- `no_answer_failure_case.md`
- `public_sources/retrieval_eval_report.md`
- `public_sources/accessible_route_answer.md`
- `public_sources/no_answer_failure_case.md`
