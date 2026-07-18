# Egocentric Local-State MLP Model Card

One-hidden-layer neural action classifier trained on the same fixed-seed A* demonstrations and evaluated on the same disjoint holdout as the other learned policies.

## Observation Contract

- Agent-centered 5x5 local window with channels for obstacle, restricted_zone, worker_zone, slow_zone, object, named_zone, current_subgoal_in_view, out_of_bounds.
- Global task and navigation values: task_deliver, task_inspect, task_charge, carrying, battery_ratio, step_ratio, relative_subgoal_x, relative_subgoal_y, subgoal_distance_x, subgoal_distance_y.
- 210 numeric inputs in total.
- Obstacles and zones outside the local window are hidden from the classifier, while relative subgoal geometry remains available.
- Inputs come directly from simulator state, not cameras or a learned perception model.

## Model And Output

- StandardScaler followed by an MLPClassifier with hidden layers [64].
- Action classes: charge, drop, inspect, move_down, move_left, move_right, move_up, pick.
- The optional safety filter applies full simulator rules after classification; it can therefore reject hazards that the local observation did not expose.

## Measured Result

- Holdout expert-action accuracy: 0.834.
- Holdout expert-action macro-F1: 0.904.
- Raw closed-loop success rate: 0.573.
- Filtered closed-loop success rate: 0.76.
- Filter interventions: 943.
- Agent-centered encoding improves substantially over the world-frame flattened raster. The filtered result also depends heavily on hand-authored simulator constraints and is not attributable to the classifier alone.

## Not Demonstrated

This model has no camera input, learned perception, convolution, recurrence, memory, uncertainty model, language embedding, reinforcement learning, or physics-state input. The separate downstream MuJoCo command replay is not ROS, sim-to-real, hardware-control, or physical-safety validation.
