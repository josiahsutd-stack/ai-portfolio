# Workflow Evaluation

The local eval script runs deterministic tasks over synthetic local documents.

```bash
python experiments/deterministic-research-workflow/scripts/evaluate_workflow.py
```

Generated artifacts:

- `demo_outputs/workflow_eval_summary.json`
- `demo_outputs/workflow_eval_report.md`
- `demo_outputs/sample_trace.json`

Measured signals:

- citation rate
- approval gate rate
- unsupported task handling
- no-evidence handling
- tool error handling
- traces written

These checks cover the six bundled synthetic tasks only. They do not measure open-ended research quality or external tool use.
