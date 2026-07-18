# MLOps Evaluation

The local eval script trains and evaluates a scikit-learn model on synthetic churn data.

```bash
python experiments/mlops-model-serving-monitoring/scripts/evaluate_model.py
```

Generated artifacts:

- `demo_outputs/model_eval_summary.json`
- `demo_outputs/model_eval_report.md`
- `demo_outputs/drift_report.md`
- `demo_outputs/sample_prediction_log.json`

Measured signals:

- accuracy, precision, recall, F1, ROC AUC, and Brier score
- schema version and feature metadata
- prediction logging format
- drift simulation and top drifted features

This is local ML engineering evidence, not production monitoring evidence.
