# Imitation-Policy Holdout Evaluation

Fixed-seed procedural construction-site simulation. All three learned models use the same expert demonstrations and disjoint holdout scenarios. This is not a learned foundation VLA or robot deployment.

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
| Egocentric 5x5 local state + 64-unit MLP | 210 | 0.834 | 0.904 |

Agent-centered local encoding recovers 0.356 action accuracy over the world-frame raster and trails the engineered-state model by 0.021. Both semantic encodings are generated from simulator state; they are not camera pixels or learned perception features.

## Closed-Loop Holdout Results

| Policy | Success rate | Avg steps | Avg reward | Unsafe action rate | Task error rate | Blocked actions | Interventions |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Engineered-state RF, raw | 0.646 | 24.969 | -15.352 | 0.674 | 0.0 | 1616 | 0 |
| Engineered-state RF, filtered | 0.698 | 22.75 | -0.222 | 0.0 | 0.0 | 0 | 692 |
| Egocentric local-state MLP, raw | 0.573 | 28.969 | -16.891 | 0.595 | 0.064 | 1654 | 0 |
| Egocentric local-state MLP, filtered | 0.76 | 23.198 | 0.14 | 0.0 | 0.0 | 0 | 943 |
| Deterministic A* reference | 1.0 | 9.875 | 2.771 | 0.0 | 0.0 | 0 | 0 |
| Semantic-raster MLP, raw | 0.031 | 53.573 | -41.293 | 0.682 | 0.186 | 3507 | 0 |
| Semantic-raster MLP, filtered | 0.292 | 43.531 | -4.773 | 0.0 | 0.0 | 0 | 3529 |

## Interpretation

- Action accuracy is measured on expert states; closed-loop success is the stronger test because policy errors change later states.
- Each raw learned policy exposes model errors without repair.
- Each shielded variant rejects unsafe or task-invalid actions but does not receive an expert route toward the task goal; charger-only recovery is separate.
- The flattened-raster MLP underperforms the engineered-state random forest. This negative result is retained because it shows that adding a neural network does not automatically improve a small-data spatial-control problem.
- Centering a local semantic window on the agent recovers most of the raster MLP's action accuracy and produces the strongest filtered learned-policy success, despite hiding hazards outside the 5x5 window.
- The egocentric policy still has weaker raw completion than the engineered-state policy and depends on many filter interventions. Filtered success is not model-only safety or control evidence.
- Neither MLP has convolution, temporal memory, camera input, or learned perception; neither establishes multimodal reasoning or VLA capability.
- The deterministic A* policy is an oracle-style planning reference, not a learned baseline.
- Results apply only to this small 2D procedural simulator.
