# Semantic-Raster MLP Model Card

One-hidden-layer neural action classifier trained on the same fixed-seed A* demonstrations and evaluated on the same disjoint holdout as the engineered-state random forest. It is preserved as a measured negative baseline.

## Inputs

- 7x7 fully observable semantic grids with channels for agent, current_subgoal, obstacle, restricted_zone, worker_zone, slow_zone, object, named_zone.
- Global features: task_deliver, task_inspect, task_charge, carrying, battery_ratio, step_ratio.
- 398 flattened numeric values in total.
- The raster is rendered from privileged simulator state, not captured by a camera or inferred by a perception model.

## Model And Output

- StandardScaler followed by an MLPClassifier with hidden layers [64].
- Action classes: charge, drop, inspect, move_down, move_left, move_right, move_up, pick.
- The optional safety filter ranks model probabilities and rejects unsafe or task-invalid actions.

## Measured Result

- Holdout expert-action accuracy: 0.478.
- Holdout expert-action macro-F1: 0.454.
- Shielded closed-loop success rate: 0.292.
- This is weaker than the engineered-state random forest on the shared holdout. The likely contributors are limited demonstrations, flattening of the grid, and the absence of convolutional spatial bias.

## Not Demonstrated

This model does not establish camera perception, visual grounding, language embeddings, a convolutional policy, a multimodal transformer, reinforcement learning, or a foundation VLA. It does not consume physics state; the separate downstream MuJoCo command replay is not ROS, sim-to-real, hardware-control, or physical-safety validation.
