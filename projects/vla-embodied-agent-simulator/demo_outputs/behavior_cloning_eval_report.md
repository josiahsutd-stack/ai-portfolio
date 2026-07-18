# Behavior-Cloning Holdout Evaluation

Fixed-seed procedural construction-site simulation. Train and holdout scenario IDs are disjoint. This is not a learned foundation VLA or robot deployment.

## Dataset And Action Metrics

- Training scenarios: 24
- Holdout scenarios: 24
- Expert training steps: 241
- Holdout expert steps: 226
- Holdout expert-action accuracy: 0.863
- Holdout expert-action macro-F1: 0.922

## Closed-Loop Holdout Results

| Policy | Success rate | Avg steps | Avg reward | Unsafe action rate | Task error rate | Blocked actions | Interventions |
| --- | --- | --- | --- | --- | --- | --- | --- |
| behavior_cloning_raw | 0.5 | 31.792 | -22.767 | 0.74 | 0.0 | 565 | 0 |
| behavior_cloning_shielded | 0.625 | 26 | -1.125 | 0.0 | 0.0 | 0 | 207 |
| safety_shielded | 1.0 | 9.417 | 2.808 | 0.0 | 0.0 | 0 | 0 |

## Interpretation

- Action accuracy is measured on expert states; closed-loop success is the stronger test because policy errors change later states.
- The raw behavior-cloning policy exposes model errors without repair.
- The shielded variant rejects unsafe or task-invalid actions but does not receive an expert route toward the task goal; charger-only recovery is separate.
- The deterministic A* policy is an oracle-style planning reference, not a learned baseline.
- Results apply only to this small 2D procedural simulator.
