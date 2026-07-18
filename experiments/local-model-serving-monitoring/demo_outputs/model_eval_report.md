# Local Model Evaluation Report

Synthetic local evaluation for the Local Model Serving and Monitoring Scaffold.

## Model Metrics

- accuracy: 1.0
- precision: 1.0
- recall: 1.0
- f1: 1.0
- roc_auc: 1.0
- brier_score: 0.002

## Artifact Metadata

- model_version: demo-v2
- schema_version: demo-churn-schema-v1
- train_rows: 135
- test_rows: 45

## Drift Simulation

- drift_detected: True
- top_drifted_features: usage_score

## Boundaries

- Synthetic churn data only.
- Local joblib and JSON artifact files only.
- Not production monitoring and not a real customer-retention decision system.
