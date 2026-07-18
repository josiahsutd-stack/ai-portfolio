# Construction Embodied Agent Simulator: System Card

## Intended Use

This project is a local construction-site embodied-agent simulator. It is intended for inspecting language-to-task parsing, behavior cloning over structured state, constrained route planning, action filtering, reward design, and trace-based evaluation.

## Not Intended For

- Real robot operation.
- Physical safety certification.
- ROS, SLAM, perception, or hardware integration claims.
- Proof that a learned policy works in the physical world.
- Foundation vision-language-action model evaluation.

## Safety Controls In Scope

- Invalid action rejection.
- Obstacle, restricted-zone, and worker-proximity checks.
- Battery and timeout handling.
- Ranked-action filtering with intervention counts.
- Repeatable policy evaluation across fixed-seed procedural train and holdout splits.

## Evaluation

The included evaluation compares deterministic A* reference behavior, raw random-forest behavior cloning, and the same learned policy with a safety filter on 24 disjoint holdout scenarios. It reports action accuracy and macro-F1 separately from closed-loop success, unsafe-action rate, task-error rate, interventions, and failure traces. A smaller hand-authored suite retains random, naive-language, and safety-shielded regression baselines.

## Main Risk

The simulator demonstrates model fitting, closed-loop evaluation, and explicit safety constraints inside a small structured grid. It must not be presented as evidence of deployed robotics ownership, perception capability, sim-to-real transfer, or validated physical safety.
