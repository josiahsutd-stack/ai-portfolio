# Construction Embodied Agent Limitations

## Model Boundary

- The learned policies are a random forest over 24 engineered values, a one-hidden-layer MLP over 398 world-raster values, and a one-hidden-layer MLP over 210 egocentric local-state values.
- The semantic raster is produced from fully observable simulator state. It is not image input or a perception output.
- None of the models is a foundation VLA, multimodal transformer, convolutional visual policy, or reinforcement-learning agent.
- Language parsing is rule-based and covers three task families.
- Expert labels come from the simulator's deterministic A* planner.

## Data Boundary

- Training and holdout data are synthetic 7x7 procedural grids.
- There are 192 training and 96 holdout scenarios with 1,830 and 948 expert steps respectively.
- Fixed seeds support reproducibility but not broad environment coverage.
- No human demonstrations, real robots, customers, employers, or construction projects supplied data.

## Environment Boundary

- The environment is discrete. The egocentric classifier has partial spatial observability, but relative subgoal geometry remains globally available and its action filter retains full-state rule access.
- There is no camera perception, observation noise, temporal memory, dynamics, physics, localization, mapping, manipulation, communication delay, or moving-worker model.
- Safety checks are hand-authored simulator constraints.
- Evaluation does not establish physical safety or compliance with robotics standards.

## Evaluation Boundary

- Expert-state action accuracy overestimates closed-loop reliability for both models.
- The raw random forest succeeds on `0.646` of holdout layouts and attempts unsafe actions at a `0.674` rate.
- The raw raster MLP succeeds on `0.031` and attempts unsafe actions at a `0.682` rate.
- The raw egocentric MLP succeeds on `0.573` and attempts unsafe actions at a `0.595` rate.
- Filtering reduces observed unsafe-action rates to `0.000`; completion is `0.698` for the random forest, `0.292` for the world-raster MLP, and `0.760` for the egocentric MLP.
- The raster MLP requires 3,529 interventions; its filtered result depends heavily on hand-authored constraints.
- The egocentric MLP requires 943 interventions. Its best learned-policy completion also depends on full-state hand-authored constraints.
- A* has full map access and is an oracle-style reference.
- These metrics are not comparable to standard robotics benchmarks without a shared environment and protocol.

## Deployment Boundary

No ROS, Isaac Sim, Gazebo, SLAM, motion control, robot hardware, sim-to-real transfer, field test, deployment, or physical-safety evidence is claimed.
