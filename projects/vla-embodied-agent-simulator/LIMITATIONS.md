# Construction Embodied Agent Limitations

## Model Boundary

- The learned policy is a random-forest action classifier over 24 engineered structured-state features.
- It is not a foundation VLA, multimodal transformer, deep policy, or reinforcement-learning agent.
- Language parsing is rule-based and covers three task families.
- Expert labels come from the simulator's deterministic A* planner.

## Data Boundary

- Training and holdout data are procedurally generated 7x7 grids.
- There are 24 train and 24 holdout scenarios.
- Fixed seeds make regression evidence reproducible but do not provide broad distribution coverage.
- No human demonstration, real robot, customer, employer, or construction-project data are included.

## Environment Boundary

- The environment is fully observable and discrete.
- There is no perception noise, partial observability, dynamics, physics, localization, mapping, manipulation, communication delay, or moving worker model.
- Safety checks are hand-authored simulator constraints.
- The evaluation does not establish physical safety or compliance with robotics standards.

## Evaluation Boundary

- Action accuracy is evaluated on expert states and overestimates closed-loop reliability.
- The raw policy's high unsafe-action rate shows substantial distribution-shift failure.
- The action filter eliminates observed simulator violations but completes only `0.625` of holdout tasks.
- A* has full map access and should be read as an oracle-style reference.
- None of the metrics are comparable to a standard robotics benchmark without a shared environment and protocol.

## Deployment Boundary

No ROS, Isaac Sim, Gazebo, SLAM, motion-control, safety-controller, robot-hardware, sim-to-real, field-test, or deployment evidence is claimed.
