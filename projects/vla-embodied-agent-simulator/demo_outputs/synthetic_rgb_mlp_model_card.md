# Synthetic RGB Observation MLP Model Card

One-hidden-layer action classifier fitted to rendered egocentric RGB crops and the same bounded task/navigation telemetry used by the semantic local-state baseline.

## Observation Contract

- 10x10 RGB image representing an agent-centered 5x5 crop.
- Additional values: task_deliver, task_inspect, task_charge, carrying, battery_ratio, step_ratio, relative_subgoal_x, relative_subgoal_y, subgoal_distance_x, subgoal_distance_y.
- 310 flattened inputs in total.
- Training appearances: day, overcast; standard holdout: day; unseen shifted holdout: worklight.
- The classifier receives pixels rather than semantic channels, but the renderer creates clean pixels directly from privileged simulator state.

## Model And Output

- StandardScaler followed by an MLPClassifier with hidden layers [64].
- Action classes: charge, drop, inspect, move_down, move_left, move_right, move_up, pick.
- 1830 expert states become 3660 appearance-variant training examples.
- The optional filter applies full simulator rules after classification and can see hazards outside the RGB crop.

## Measured Result

- Standard holdout action accuracy / macro-F1: 0.813 / 0.805.
- Shifted holdout action accuracy / macro-F1: 0.417 / 0.429.
- Mean-pixel ablation action accuracy / macro-F1: 0.474 / 0.464.
- Standard-minus-ablation accuracy: 0.34.
- Standard raw / filtered success: 0.635 / 0.719.
- Shifted raw / filtered success: 0.0 / 0.427.
- Standard / shifted filter interventions: 965 / 3315.

## Not Demonstrated

This model does not establish physical-camera perception, object detection, segmentation, depth estimation, calibration, occlusion handling, realistic sensor noise, convolutional visual learning, language grounding, a foundation VLA, physics, ROS, sim-to-real transfer, hardware control, or physical-safety validation.
