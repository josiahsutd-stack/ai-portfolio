# Construction Embodied Agent Limitations

## Model Boundary

- The learned policies are a random forest over 24 engineered values, a one-hidden-layer MLP over 398 world-raster values, a one-hidden-layer MLP over 210 egocentric local-state values, and a one-hidden-layer MLP over 300 RGB values plus ten task/navigation values.
- The semantic rasters and RGB images are produced from fully observable simulator state. The RGB classifier receives pixels, but the renderer is not a physical or photorealistic simulated camera.
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
- MuJoCo replays planar position targets with rigid contacts for a 12-scenario holdout subset. It is not the learned policy environment and has no mobile-base kinematics, actuator identification, contact-force safety model, localization, mapping, manipulation, communication delay, or moving-worker model.
- There is no physical-camera perception, detection, segmentation, depth, calibration, blur, occlusion, or realistic sensor noise.
- Safety checks are hand-authored simulator constraints.
- Evaluation does not establish physical safety or compliance with robotics standards.

## Evaluation Boundary

- Expert-state action accuracy overestimates closed-loop reliability for both models.
- The raw random forest succeeds on `0.646` of holdout layouts and attempts unsafe actions at a `0.674` rate.
- The raw raster MLP succeeds on `0.031` and attempts unsafe actions at a `0.682` rate.
- The raw egocentric MLP succeeds on `0.573` and attempts unsafe actions at a `0.595` rate.
- The raw standard RGB MLP succeeds on `0.635` with unsafe-action rate `0.041` and task-error rate `0.489`.
- Under the unseen work-light palette, RGB action accuracy falls from `0.813` to `0.417` and raw completion falls from `0.635` to `0.000`.
- Mean-pixel ablation lowers action accuracy from `0.813` to `0.474`, demonstrating pixel dependence but not transferable perception or interpretable visual grounding.
- Filtering reduces observed unsafe-action rates to `0.000`; completion is `0.698` for the random forest, `0.292` for the world-raster MLP, `0.760` for the egocentric MLP, `0.719` for standard RGB, and `0.427` for shifted RGB.
- The raster MLP requires 3,529 interventions; its filtered result depends heavily on hand-authored constraints.
- The egocentric MLP requires 943 interventions. Its best learned-policy completion also depends on full-state hand-authored constraints.
- Standard and shifted RGB require 965 and 3,315 interventions respectively. The shifted result shows that the filter can partially mask severe appearance brittleness.
- A* has full map access and is an oracle-style reference.
- These metrics are not comparable to standard robotics benchmarks without a shared environment and protocol.
- In planar replay, the raw egocentric policy contacts named rigid geometry on 51 of 150 movement commands (`0.340`); filtered egocentric and A* traces record zero contacts and reach all targets on 148 and 98 movement commands respectively.
- Restricted and worker cells are rigid collision proxies. Contact counts do not model human impact, injury, force limits, or site dynamics.
- Blocked commands are returned to the discrete result cell before the next command. That alignment reset is not autonomous recovery or closed-loop physics control.

## Deployment Boundary

No ROS, Isaac Sim, Gazebo, mobile-base controller, SLAM, robot hardware, sim-to-real transfer, field test, deployment, or physical-safety evidence is claimed.
