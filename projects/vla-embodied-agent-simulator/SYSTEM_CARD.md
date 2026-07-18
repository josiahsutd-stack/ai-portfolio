# Construction Embodied Agent Simulator: System Card

## Intended Use

This local simulator supports inspection of task parsing, observation encoding, supervised imitation, constrained route planning, action filtering, reward design, and trace-based evaluation.

## Not Intended For

- Real robot operation or physical safety decisions.
- ROS, SLAM, perception, hardware, or sim-to-real claims.
- Proof that a learned policy works on a construction site.
- Foundation vision-language-action evaluation.

## Models In Scope

1. A random-forest action classifier over 24 engineered state features.
2. A one-hidden-layer MLP over eight fully observable 7x7 semantic state channels plus six global features.

The second model does not consume images. It is included because it underperforms the engineered baseline and exposes a representation and data-scale limitation.

## Safety Controls In Scope

- Invalid action rejection.
- Obstacle, restricted-zone, and worker-proximity checks.
- Battery and timeout handling.
- Ranked-action filtering with intervention counts.
- Repeatable evaluation across fixed-seed procedural train and holdout splits.

## Evaluation

Both learned models train on 192 synthetic scenarios and are evaluated on the same 96 disjoint holdout scenarios. Reports separate expert-state action accuracy from closed-loop success, unsafe-action rate, task-error rate, interventions, and failure traces. A deterministic A* planner is retained as a full-map reference, not a learned baseline.

## Main Risk

The action filter can make weak learned behavior look safer than it is. The published report therefore includes raw rollouts, intervention counts, failed episodes, and explicit model boundaries. None of these results establish perception, physical safety, or deployment readiness.
