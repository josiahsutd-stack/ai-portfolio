# Behavior-Cloning Policy Model Card

Random-forest action classifier trained on fixed-seed expert A* demonstrations from procedural 7x7 construction-site grids.

## Inputs

- 24 numeric state features covering task phase, carrying state, battery, agent/subgoal geometry, local movement safety, and distance change.
- No image, depth, point-cloud, language embedding, or robot telemetry input.

## Output

- Action classes: charge, drop, inspect, move_down, move_left, move_right, move_up, pick.
- The safety-filtered policy ranks model probabilities, rejects unsafe or task-invalid actions, and invokes a charger-only reserve controller before battery depletion.

## Training Boundary

- Expert labels come from the simulator's A* planner.
- Train and holdout scenario seeds and IDs are disjoint.
- The joblib binary is generated locally and ignored by Git; deterministic metrics and reports are versioned.

## Not Demonstrated

This model is not a foundation VLA, does not consume pixels or free-form language embeddings, and has no physics, ROS, sim-to-real, hardware, or physical-safety validation.
