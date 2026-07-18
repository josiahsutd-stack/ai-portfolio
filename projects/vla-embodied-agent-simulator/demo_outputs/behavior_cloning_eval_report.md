# Imitation-Policy Holdout Evaluation

Fixed-seed procedural construction-site simulation. Four learned policy families use the same expert demonstrations and disjoint holdout scenarios. The RGB model receives two training appearances; its unseen work-light appearance is reported separately. This is not a learned foundation VLA or robot deployment.

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
| Synthetic 10x10 RGB crop + 10 telemetry values + 64-unit MLP | 310 | 0.813 | 0.805 |
| Same RGB model, unseen worklight palette | 310 | 0.417 | 0.429 |
| Same RGB model, pixels replaced by training means | 10 active telemetry values | 0.474 | 0.464 |

Agent-centered local encoding recovers 0.356 action accuracy over the world-frame raster and trails the engineered-state model by 0.021. The RGB policy consumes rendered pixels, but those pixels are generated deterministically from privileged simulator state rather than captured by a camera.

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
| Synthetic RGB MLP, raw | 0.635 | 26.99 | -6.184 | 0.041 | 0.489 | 105 | 0 |
| Synthetic RGB MLP, filtered | 0.719 | 23.969 | -0.121 | 0.0 | 0.0 | 0 | 965 |
| Synthetic RGB MLP, shifted appearance, raw | 0.0 | 55 | -34.135 | 0.472 | 0.335 | 2490 | 0 |
| Synthetic RGB MLP, shifted appearance, filtered | 0.427 | 42.792 | -4.575 | 0.0 | 0.0 | 0 | 3315 |

## Interpretation

- Action accuracy is measured on expert states; closed-loop success is the stronger test because policy errors change later states.
- Each raw learned policy exposes model errors without repair.
- Each shielded variant rejects unsafe or task-invalid actions but does not receive an expert route toward the task goal; charger-only recovery is separate.
- The flattened-raster MLP underperforms the engineered-state random forest. This negative result is retained because it shows that adding a neural network does not automatically improve a small-data spatial-control problem.
- Centering a local semantic window on the agent recovers most of the raster MLP's action accuracy and produces the strongest filtered learned-policy success, despite hiding hazards outside the 5x5 window.
- The egocentric policy still has weaker raw completion than the engineered-state policy and depends on many filter interventions. Filtered success is not model-only safety or control evidence.
- The RGB policy reports both its standard appearance and an unseen palette shift. Any degradation remains visible rather than being averaged into the standard result.
- Replacing every holdout pixel with its training-set mean reduces action accuracy by 0.34. This ablation shows that the image contributes predictive information beyond the ten telemetry values.
- The RGB renderer removes direct semantic channels at the classifier boundary, but it still maps privileged grid state into clean synthetic pixels. It does not model detection, segmentation, depth, calibration, occlusion, or sensor noise.
- No MLP has convolution, temporal memory, a physical camera, or learned language conditioning; none establishes multimodal reasoning or foundation-VLA capability.
- The deterministic A* policy is an oracle-style planning reference, not a learned baseline.
- Results apply only to this small 2D procedural simulator.
