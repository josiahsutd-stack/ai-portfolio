# Agent Evaluation

The local eval script runs deterministic tasks over synthetic local documents.

```bash
python projects/agentic-research-ops-assistant/scripts/evaluate_agent.py
```

Generated artifacts:

- `demo_outputs/agent_eval_summary.json`
- `demo_outputs/agent_eval_report.md`
- `demo_outputs/sample_trace.json`

Measured signals:

- citation rate
- approval gate rate
- unsupported task handling
- no-evidence handling
- tool error handling
- traces written

This is a local workflow evaluation, not proof of autonomous research capability.
