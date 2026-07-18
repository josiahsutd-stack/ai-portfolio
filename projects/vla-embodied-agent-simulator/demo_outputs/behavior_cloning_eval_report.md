# Imitation-Policy Holdout Evaluation

Fixed-seed procedural construction-site simulation. Both learned policies use the same expert demonstrations and disjoint holdout scenarios. This is not a learned foundation VLA or robot deployment.

## Shared Evaluation Protocol

- Training scenarios: 192
- Holdout scenarios: 96
- Expert training steps: 1830
- Holdout expert steps: 948
- Holdout action metrics are measured on expert-visited states.
- Closed-loop metrics measure compounding errors after each policy takes control.

## Representation Comparison

| Policy input and model | Features | Holdout action accuracy | Holdout macro-F1 |
| --- | ---: | ---: | ---: |
| Engineered state + random forest | 24 | 0.855 | 0.916 |
| Flattened semantic raster + 64-unit MLP | 398 | 0.478 | 0.454 |

The engineered-state baseline leads action accuracy by 0.377. The raster channels are generated from fully observable simulator state; they are not camera pixels or learned perception features.

## Closed-Loop Holdout Results

| Policy | Success rate | Avg steps | Avg reward | Unsafe action rate | Task error rate | Blocked actions | Interventions |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Engineered-state RF, raw | 0.646 | 24.969 | -15.352 | 0.674 | 0.0 | 1616 | 0 |
| Engineered-state RF, filtered | 0.698 | 22.75 | -0.222 | 0.0 | 0.0 | 0 | 692 |
| Deterministic A* reference | 1.0 | 9.875 | 2.771 | 0.0 | 0.0 | 0 | 0 |
| Semantic-raster MLP, raw | 0.031 | 53.573 | -41.293 | 0.682 | 0.186 | 3507 | 0 |
| Semantic-raster MLP, filtered | 0.469 | 44.375 | 9.504 | 0.0 | 0.0 | 0 | 3617 |

## Interpretation

- Action accuracy is measured on expert states; closed-loop success is the stronger test because policy errors change later states.
- Each raw learned policy exposes model errors without repair.
- Each shielded variant rejects unsafe or task-invalid actions but does not receive an expert route toward the task goal; charger-only recovery is separate.
- The flattened-raster MLP underperforms the engineered-state random forest. This negative result is retained because it shows that adding a neural network does not automatically improve a small-data spatial-control problem.
- The MLP has no convolutional spatial inductive bias and does not establish visual perception, multimodal reasoning, or VLA capability.
- The deterministic A* policy is an oracle-style planning reference, not a learned baseline.
- Results apply only to this small 2D procedural simulator.
